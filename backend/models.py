from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Parent(db.Model):
    """家长账户"""
    __tablename__ = 'parents'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    practice_to_game_ratio = db.Column(db.Float, default=1.0)  # 1分鐘練琴兌換1分鐘遊戲時間
    
    children = db.relationship('Child', backref='parent', lazy=True, cascade='all, delete-orphan')
    game_awards = db.relationship('GameAward', backref='parent', lazy=True)

class Child(db.Model):
    """孩子账户"""
    __tablename__ = 'children'

    id = db.Column(db.String(20), primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    practice_records = db.relationship('PracticeRecord', backref='child', lazy=True, cascade='all, delete-orphan')
    game_balance = db.Column(db.Integer, default=0)  # 游戏时间积分

class PracticeRecord(db.Model):
    """练琴记录"""
    __tablename__ = 'practice_records'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.String(20), db.ForeignKey('children.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time)  # 练琴时间
    practice_minutes = db.Column(db.Integer, nullable=False)  # 分钟，以5分钟为单位
    notes = db.Column(db.Text)  # 备注：今天练的内容
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    
    __table_args__ = (db.UniqueConstraint('child_id', 'date', name='unique_daily_record'),)

class GameAward(db.Model):
    """游戏时间奖励记录"""
    __tablename__ = 'game_awards'
    
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    child_id = db.Column(db.String(20), db.ForeignKey('children.id'), nullable=False)
    game_minutes = db.Column(db.Integer, nullable=False)  # 发放的游戏时间（分钟）
    reason = db.Column(db.String(255))  # 原因
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    child = db.relationship('Child', backref='received_awards', foreign_keys=[child_id])

class GameRequest(db.Model):
    """游戏时间申请/使用记录"""
    __tablename__ = 'game_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.String(20), db.ForeignKey('children.id'), nullable=False)
    game_minutes = db.Column(db.Integer, nullable=False)  # 申请的游戏时间（分钟），以15分钟为单位
    request_date = db.Column(db.DateTime, default=datetime.utcnow)  # 申请时间
    status = db.Column(db.String(20), default='approved')  # approved=已批准(已扣除)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    child = db.relationship('Child', backref='game_requests', foreign_keys=[child_id])
