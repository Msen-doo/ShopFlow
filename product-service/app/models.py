# product-service/app/models.py
from . import db
import uuid
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'

    id          = db.Column(db.String(36), primary_key=True,
                            default=lambda: str(uuid.uuid4()))
    name        = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price       = db.Column(db.Numeric(10, 2), nullable=False)
    stock       = db.Column(db.Integer, nullable=False, default=0)
    deleted     = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':          self.id,
            'name':        self.name,
            'description': self.description,
            'price':       float(self.price),
            'stock':       self.stock,
            'created_at':  self.created_at.isoformat()
        }