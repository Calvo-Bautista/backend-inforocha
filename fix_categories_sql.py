import sys
import os
from sqlalchemy import text

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal

def fix_categories_sql():
    db = SessionLocal()
    try:
        # Check current values
        print("Before fix:")
        result = db.execute(text("SELECT DISTINCT category FROM products"))
        for row in result:
            print(f"'{row[0]}'")
            
        # Update values with LIKE to catch potential issues
        print("Updating with LIKE...")
        db.execute(text("UPDATE products SET category = 'toner' WHERE category LIKE '%TONER%'"))
        db.execute(text("UPDATE products SET category = 'cartucho' WHERE category LIKE '%CARTUCHO%'"))
        db.execute(text("UPDATE products SET category = 'drum' WHERE category LIKE '%DRUM%'"))
        db.execute(text("UPDATE products SET category = 'repuesto' WHERE category LIKE '%REPUESTO%'"))
        
        # Also handle Title Case if present
        db.execute(text("UPDATE products SET category = 'toner' WHERE category = 'Toner'"))
        db.execute(text("UPDATE products SET category = 'cartucho' WHERE category = 'Cartucho'"))
        db.execute(text("UPDATE products SET category = 'drum' WHERE category = 'Drum'"))
        
        db.commit()
        
        # Check after fix
        print("After fix:")
        result = db.execute(text("SELECT DISTINCT category FROM products"))
        for row in result:
            print(f"'{row[0]}'")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_categories_sql()
