from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from sqlalchemy.exc import OperationalError, ProgrammingError, IntegrityError
import os
import time

db  = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['JWT_SECRET_KEY']          = os.environ['JWT_SECRET_KEY']

    db.init_app(app)
    jwt.init_app(app)

    from .routes import product_bp
    app.register_blueprint(product_bp, url_prefix='/api/products')

    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200

    with app.app_context():
        from . import models

        # Wait for Postgres to be ready to accept connections — depends_on
        # only waits for the container to start, not for the DB to be up.
        for attempt in range(10):
            try:
                db.engine.connect().close()
                break
            except OperationalError:
                if attempt == 9:
                    raise
                time.sleep(1)

        try:
            db.create_all()
        except (ProgrammingError, IntegrityError):
            # Another gunicorn worker won the race to create the tables
            # on a fresh database — safe to ignore, tables now exist.
            db.session.rollback()

    return app