# order-service/app/routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import db
from .models import Order, OrderItem
import boto3, json, os

order_bp = Blueprint('orders', __name__)

# Only create SQS client if the env var exists
# (so the service still starts locally without AWS)
SQS_QUEUE_URL = os.environ.get('SQS_ORDER_QUEUE_URL')

def get_sqs():
    return boto3.client('sqs', region_name=os.environ.get(
                         'AWS_REGION', 'eu-west-1'))

# POST place an order
@order_bp.route('/', methods=['POST'])
@jwt_required()
def place_order():
    uid  = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('items'):
        return jsonify({'error': 'items are required'}), 400

    # calculate total
    total = sum(
        float(i['unit_price']) * int(i['quantity'])
        for i in data['items']
    )

    # create order record
    order = Order(user_id=uid, total=total, status='PENDING')
    db.session.add(order)
    db.session.flush()  # populate order.id before it's referenced below

    # create order item records
    order_items_payload = []
    for i in data['items']:
        item = OrderItem(
            order_id   = order.id,
            product_id = i['product_id'],
            quantity   = i['quantity'],
            unit_price = i['unit_price']
        )
        db.session.add(item)
        order_items_payload.append({
            'product_id': i['product_id'],
            'quantity':   i['quantity']
        })

    db.session.commit()

    # publish event to SQS (only if queue URL is configured)
    if SQS_QUEUE_URL:
        try:
            get_sqs().send_message(
                QueueUrl               = SQS_QUEUE_URL,
                MessageBody            = json.dumps({
                    'order_id': order.id,
                    'user_id':  uid,
                    'items':    order_items_payload
                }),
                MessageGroupId         = 'orders',
                MessageDeduplicationId = order.id
            )
        except Exception as e:
            # log but do not fail the order
            print(f'SQS publish failed: {e}')

    return jsonify({
        'order_id': order.id,
        'status':   'PENDING',
        'total':    float(total)
    }), 201

# GET all orders for logged-in user
@order_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    uid    = get_jwt_identity()
    orders = Order.query.filter_by(user_id=uid) \
                        .order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders]), 200

# GET single order
@order_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    uid   = get_jwt_identity()
    order = Order.query.filter_by(
                id=order_id, user_id=uid).first_or_404()
    return jsonify(order.to_dict()), 200
