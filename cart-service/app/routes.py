# cart-service/app/routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import redis
import os

cart_bp  = Blueprint('cart', __name__)

# Connect to Redis
# If REDIS_URL is not set, fall back to localhost for development
r = redis.Redis.from_url(
    os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    decode_responses=True
)

CART_TTL = 86400  # 24 hours in seconds

def cart_key(user_id):
    """Build the Redis key for a user's cart."""
    return f'cart:{user_id}'


# GET — view current cart
@cart_bp.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    uid   = get_jwt_identity()
    items = r.hgetall(cart_key(uid))  # returns {product_id: quantity}

    if not items:
        return jsonify({
            'items':      {},
            'item_count': 0,
            'message':    'cart is empty'
        }), 200

    item_count = sum(int(q) for q in items.values())

    return jsonify({
        'items':      items,
        'item_count': item_count
    }), 200


# POST — add item to cart
@cart_bp.route('/items', methods=['POST'])
@jwt_required()
def add_item():
    uid  = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('product_id') or not data.get('quantity'):
        return jsonify({'error': 'product_id and quantity are required'}), 400

    product_id = data['product_id']
    quantity   = int(data['quantity'])

    if quantity <= 0:
        return jsonify({'error': 'quantity must be greater than zero'}), 400

    # hset adds or updates the field in the Redis hash
    r.hset(cart_key(uid), product_id, quantity)

    # reset the 24-hour expiry timer every time cart is touched
    r.expire(cart_key(uid), CART_TTL)

    return jsonify({
        'message':    'item added to cart',
        'product_id': product_id,
        'quantity':   quantity
    }), 200


# PUT — update quantity of an existing item
@cart_bp.route('/items/<product_id>', methods=['PUT'])
@jwt_required()
def update_item(product_id):
    uid  = get_jwt_identity()
    data = request.get_json()

    if not data or 'quantity' not in data:
        return jsonify({'error': 'quantity is required'}), 400

    quantity = int(data['quantity'])

    if quantity <= 0:
        # if quantity drops to zero, remove the item entirely
        r.hdel(cart_key(uid), product_id)
        return jsonify({'message': 'item removed from cart'}), 200

    r.hset(cart_key(uid), product_id, quantity)
    r.expire(cart_key(uid), CART_TTL)

    return jsonify({
        'message':    'item updated',
        'product_id': product_id,
        'quantity':   quantity
    }), 200


# DELETE — remove one item from cart
@cart_bp.route('/items/<product_id>', methods=['DELETE'])
@jwt_required()
def remove_item(product_id):
    uid    = get_jwt_identity()
    result = r.hdel(cart_key(uid), product_id)

    if result == 0:
        return jsonify({'error': 'item not found in cart'}), 404

    return jsonify({'message': 'item removed from cart'}), 200


# DELETE — clear the entire cart
@cart_bp.route('/', methods=['DELETE'])
@jwt_required()
def clear_cart():
    uid = get_jwt_identity()
    r.delete(cart_key(uid))
    return jsonify({'message': 'cart cleared'}), 200