#!/usr/bin/env python3
"""
Database Backup Exporter
This script safely extracts all data from your live database
and saves it to a local JSON file.
"""

import os
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from models.user import User
from models.category import Category
from models.product import Product
from models.order import Order
from models.order_item import OrderItem

load_dotenv()

USER = os.getenv('MINI_MART_MYSQL_USER')
PWD = os.getenv('MINI_MART_MYSQL_PWD')
HOST = os.getenv('MINI_MART_MYSQL_HOST')
DB = os.getenv('MINI_MART_MYSQL_DB')

# Construct the URI
uri = f"mysql+pymysql://{USER}:{PWD}@{HOST}/{DB}"

def get_raw_dict(obj):
    """
    Extracts the exact raw data from the database row, 
    bypassing to_dict() so we don't lose the hashed passwords!
    """
    raw_dict = {}
    for column in obj.__table__.columns:
        val = getattr(obj, column.name)
        # Convert datetime objects to string so they can be saved in JSON
        if isinstance(val, datetime):
            raw_dict[column.name] = val.isoformat()
        else:
            raw_dict[column.name] = val
    return raw_dict

def backup_database():
    print(f"🔄 Connecting to Database at {HOST}...")
    try:
        engine = create_engine(uri, connect_args={"ssl": {}})
        Session = sessionmaker(bind=engine)
        session = Session()

        print("📦 Extracting data...")
        
        backup_data = {
            "users": [get_raw_dict(u) for u in session.query(User).all()],
            "categories": [get_raw_dict(c) for c in session.query(Category).all()],
            "products": [get_raw_dict(p) for p in session.query(Product).all()],
            "orders": [get_raw_dict(o) for o in session.query(Order).all()],
            "order_items": [get_raw_dict(oi) for oi in session.query(OrderItem).all()]
        }

        session.close()

        backup_filename = "food_mart_backup.json"
        with open(backup_filename, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=4)

        print(f"\n✅ SUCCESS! Backup saved to: {backup_filename}")
        print(f"  - Users: {len(backup_data['users'])}")
        print(f"  - Categories: {len(backup_data['categories'])}")
        print(f"  - Products: {len(backup_data['products'])}")
        print(f"  - Orders: {len(backup_data['orders'])}")
        print(f"  - Order Items: {len(backup_data['order_items'])}")
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")

if __name__ == "__main__":
    backup_database()