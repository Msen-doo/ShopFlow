# user-service/app/routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User
 
auth_bp = Blueprint('auth', __name__)
 
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'email and password required'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'email already registered'}), 409
    user = User(
        email    = data['email'],
        password = generate_password_hash(data['password'])
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id}), 201
 
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not check_password_hash(user.password, data.get('password','')):
        return jsonify({'error': 'invalid credentials'}), 401
    token = create_access_token(identity=user.id)
    return jsonify({'access_token': token}), 200
 
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user = User.query.get(get_jwt_identity())
    return jsonify(user.to_dict()), 200
