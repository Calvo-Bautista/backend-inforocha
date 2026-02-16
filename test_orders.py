import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from app.models.order import Order

def test_query():
    print("Testing Order query...")
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        orders = db.query(Order).limit(5).all()
        print(f"Successfully queried {len(orders)} orders.")
        for o in orders:
            print(f"Order {o.id}: Invoice Type={o.invoice_type}")
    except Exception as e:
        print(f"Query failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_query()
