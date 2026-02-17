
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.product import Product

def create_test_product():
    db = SessionLocal()
    try:
        # Check if product exists
        existing = db.query(Product).filter(Product.articulo == "TEST-VERIFY").first()
        if existing:
            print("Test product already exists.")
            return

        print("Creating test product...")
        new_product = Product(
            articulo="TEST-VERIFY",
            description="Verification Product",
            price=100.0,
            stock=10,
            category="repuesto"
        )
        db.add(new_product)
        db.commit()
        print("Test product created successfully.")
        
        # Verify read
        p = db.query(Product).filter(Product.articulo == "TEST-VERIFY").first()
        print(f"Verified product: Articulo={p.articulo}, Description={p.description}")
        
    except Exception as e:
        print(f"Error creating product: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_product()
