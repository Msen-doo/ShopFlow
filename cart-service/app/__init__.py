# cart-service/app/__init__.py
from flask import Flask
from flask_jwt_extended import JWTManager
import os

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']

    jwt.init_app(app)

    from .routes import cart_bp
    app.register_blueprint(cart_bp, url_prefix='/cart')

    return app