from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Parent(db.Model):
    """Parent account"""
    __tablename__ = 'parents'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    practice_to_game_ratio = db.Column(db.Float, default=1.0)  # 1 min practice = 1 reward point

    children = db.relationship('Child', backref='parent', lazy=True, cascade='all, delete-orphan')
    game_awards = db.relationship('GameAward', backref='parent', lazy=True)

class Child(db.Model):
    """Child account"""
    __tablename__ = 'children'

    id = db.Column(db.String(20), primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    practice_records = db.relationship('PracticeRecord', backref='child', lazy=True, cascade='all, delete-orphan')
    game_balance = db.Column(db.Integer, default=0)  # Game reward points balance

class PracticeRecord(db.Model):
    """Practice record"""
    __tablename__ = 'practice_records'

    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.String(20), db.ForeignKey('children.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time)  # Practice start time
    practice_minutes = db.Column(db.Integer, nullable=False)  # Duration in minutes (5-min units)
    notes = db.Column(db.Text)  # Notes: today's practice content
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)

    __table_args__ = (db.UniqueConstraint('child_id', 'date', name='unique_daily_record'),)

class GameAward(db.Model):
    """Game reward award record"""
    __tablename__ = 'game_awards'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    child_id = db.Column(db.String(20), db.ForeignKey('children.id'), nullable=False)
    game_minutes = db.Column(db.Integer, nullable=False)  # Reward points granted
    reason = db.Column(db.String(255))  # Reason for the award
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    child = db.relationship('Child', backref='received_awards', foreign_keys=[child_id])

class GameRequest(db.Model):
    """Game time redemption record"""
    __tablename__ = 'game_requests'

    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.String(20), db.ForeignKey('children.id'), nullable=False)
    game_minutes = db.Column(db.Integer, nullable=False)  # Points redeemed (15-min units)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)  # Redemption time
    status = db.Column(db.String(20), default='approved')  # approved = deducted from balance
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    child = db.relationship('Child', backref='game_requests', foreign_keys=[child_id])

class SpecialRedemption(db.Model):
    """Special redemption item set by parent for a child"""
    __tablename__ = 'special_redemptions'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    child_id = db.Column(db.String(20), db.ForeignKey('children.id'), nullable=False)
    content = db.Column(db.String(255), nullable=False)   # Item description
    points_cost = db.Column(db.Integer, nullable=False)    # Points required
    quantity = db.Column(db.Integer, nullable=True)        # Max redemptions, None = unlimited
    expires_at = db.Column(db.DateTime, nullable=True)     # Expiry date, None = no expiry
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    child = db.relationship('Child', backref='special_redemptions', foreign_keys=[child_id])
    records = db.relationship('SpecialRedemptionRecord', backref='redemption', lazy=True, cascade='all, delete-orphan')

class SpecialRedemptionRecord(db.Model):
    """Record of a child redeeming a special item"""
    __tablename__ = 'special_redemption_records'

    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.String(20), db.ForeignKey('children.id'), nullable=False)
    redemption_id = db.Column(db.Integer, db.ForeignKey('special_redemptions.id'), nullable=False)
    content = db.Column(db.String(255), nullable=False)    # Snapshot of item content at time of redeem
    points_spent = db.Column(db.Integer, nullable=False)   # Snapshot of cost at time of redeem
    redeemed_at = db.Column(db.DateTime, default=datetime.utcnow)

    child = db.relationship('Child', backref='special_redemption_records', foreign_keys=[child_id])
