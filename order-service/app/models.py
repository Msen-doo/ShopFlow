# order-service/app/models.py
from . import db
import uuid
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    id         = db.Column(db.String(36), primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    user_id    = db.Column(db.String(36), nullable=False)
    status     = db.Column(db.String(50), nullable=False,
                           default='PENDING')
    total      = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationship — one order has many items
    items      = db.relationship('OrderItem', backref='order',
                                 lazy=True)

    def to_dict(self):
        return {
            'id':         self.id,
            'user_id':    self.user_id,
            'status':     self.status,
            'total':      float(self.total),
            'created_at': self.created_at.isoformat(),
            'items':      [i.to_dict() for i in self.items]
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id         = db.Column(db.String(36), primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    order_id   = db.Column(db.String(36),
                           db.ForeignKey('orders.id'),
                           nullable=False)
    product_id = db.Column(db.String(36), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    def to_dict(self):
        return {
            'id':         self.id,
            'product_id': self.product_id,
            'quantity':   self.quantity,
            'unit_price': float(self.unit_price)
        }