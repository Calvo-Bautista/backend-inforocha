"""
Script para activar todos los productos en la base de datos
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from sqlalchemy import text

def activate_all_products():
    """Activate all products in the database"""
    db = SessionLocal()
    try:
        # Update all products to is_active = True using raw SQL
        result = db.execute(
            text("UPDATE products SET is_active = TRUE WHERE is_active IS NULL OR is_active = FALSE")
        )
        db.commit()
        
        print(f"✅ Successfully activated {result.rowcount} products")
        
        # Show all products
        products = db.execute(text("SELECT id, sku, name, is_active FROM products ORDER BY id")).fetchall()
        print(f"\n📦 Total products in database: {len(products)}")
        print("\nProducts:")
        for p in products:
            status = "✓" if p.is_active else "✗"
            print(f"  {status} [{p.id}] {p.sku} - {p.name} (Active: {p.is_active})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Activating all products...\n")
    activate_all_products()
