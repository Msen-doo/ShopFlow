# user-service/app/models.py
from . import db
import uuid
from datetime import datetime
 
class User(db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.String(36), primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    email      = db.Column(db.String(255), nullable=False, unique=True)
    password   = db.Column(db.String(255), nullable=False)  # bcrypt hash
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
 
    def to_dict(self):
        return {'id': self.id, 'email': self.email,
                'created_at': self.created_at.isoformat()}
