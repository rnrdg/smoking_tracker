from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Cigarette(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    trigger = db.Column(db.String(50), nullable=True) # e.g., "Stress", "Boredom"
    cost = db.Column(db.Float, default=0.0) # Cost in Tenge

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'trigger': self.trigger,
            'cost': self.cost
        }

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pack_price = db.Column(db.Integer, default=700) # Default price in Tenge
    pack_size = db.Column(db.Integer, default=20)   # Default size

    def to_dict(self):
        return {
            'pack_price': self.pack_price,
            'pack_size': self.pack_size
        }
