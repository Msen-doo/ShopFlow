# order-service/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os

db  = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['JWT_SECRET_KEY']          = os.environ['JWT_SECRET_KEY']

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

    from .routes import order_bp
    app.register_blueprint(order_bp, url_prefix='/orders')

    return app