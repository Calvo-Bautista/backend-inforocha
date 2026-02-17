
import sys
import os

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app.models.product import Product
from app.models.order import Order, OrderItem
# Import other models if needed to ensure they are registered
from app.models.client import Client
from app.models.user import User
from app.models.config import BusinessConfig
from app.models.client_printer import ClientPrinter

def reset_db():
    print("Dropping specific tables (Items, Orders, Products)...")
    # Drop in order of dependency: OrderItem -> Order, Product
    try:
        OrderItem.__table__.drop(bind=engine)
        print("Dropped order_items")
    except Exception as e:
        print(f"Error dropping order_items: {e}")

    try:
        Order.__table__.drop(bind=engine)
        print("Dropped orders")
    except Exception as e:
        print(f"Error dropping orders: {e}")

    try:
        Product.__table__.drop(bind=engine)
        print("Dropped products")
    except Exception as e:
        print(f"Error dropping products: {e}")
    
    print("Creating all tables (only missing ones will be created)...")
    Base.metadata.create_all(bind=engine)
    print("Tables created/verified.")
    print("Schema update complete.")

if __name__ == "__main__":
    reset_db()
