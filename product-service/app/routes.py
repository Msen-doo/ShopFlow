# product-service/app/routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from . import db
from .models import Product

product_bp = Blueprint('products', __name__)

# GET all products (paginated)
@product_bp.route('/', methods=['GET'])
def list_products():
    page  = request.args.get('page',  1,  type=int)
    limit = request.args.get('limit', 20, type=int)
    items = Product.query.filter_by(deleted=False) \
                         .paginate(page=page, per_page=limit,
                                   error_out=False)
    return jsonify({
        'items': [p.to_dict() for p in items.items],
        'total': items.total,
        'page':  items.page,
        'pages': items.pages
    }), 200

# GET single product
@product_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    p = Product.query.get_or_404(product_id)
    return jsonify(p.to_dict()), 200

# POST create product (protected)
@product_bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('price'):
        return jsonify({'error': 'name and price are required'}), 400
    p = Product(
        name        = data['name'],
        description = data.get('description', ''),
        price       = data['price'],
        stock       = data.get('stock', 0)
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201

# PUT update product (protected)
@product_bp.route('/<product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    p    = Product.query.get_or_404(product_id)
    data = request.get_json()
    if 'name'        in data: p.name        = data['name']
    if 'description' in data: p.description = data['description']
    if 'price'       in data: p.price       = data['price']
    if 'stock'       in data: p.stock       = data['stock']
    db.session.commit()
    return jsonify(p.to_dict()), 200

# DELETE soft-delete product (protected)
@product_bp.route('/<product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    p         = Product.query.get_or_404(product_id)
    p.deleted = True
    db.session.commit()
    return jsonify({'message': 'product deleted'}), 200
