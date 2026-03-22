#!/usr/bin/env python
"""數據庫初始化腳本 - 創建測試用戶"""

from app import create_app, db
from models import Parent, Child
from werkzeug.security import generate_password_hash

def init_db():
    """初始化測試數據"""
    app = create_app('development')
    
    with app.app_context():
        # 刪除所有表
        db.drop_all()
        
        # 創建所有表
        db.create_all()
        print("✅ 數據庫表已創建")
        
        # 創建測試家長
        parent = Parent(
            username='testparent',
            email='parent@example.com',
            password_hash=generate_password_hash('parent123')
        )
        db.session.add(parent)
        db.session.commit()
        print(f"✅ 家長已創建 - ID: {parent.id}, 用戶名: {parent.username}")
        
        # 創建測試子女
        child = Child(
            parent_id=parent.id,
            name='Test Child',
            age=10,
            password_hash=generate_password_hash('child123')
        )
        db.session.add(child)
        db.session.commit()
        print(f"✅ 子女已創建 - ID: {child.id}, 名稱: {child.name}")
        
        print("\n========== 測試用戶信息 ==========")
        print(f"家長登入: username='testparent', password='parent123'")
        print(f"子女登入: child_id={child.id}, password='child123'")
        print("===================================")

if __name__ == '__main__':
    init_db()
