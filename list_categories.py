import sys
import os
from sqlalchemy import text

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal

def list_categories():
    db = SessionLocal()
    try:
        # Use raw SQL to see exactly what's in the DB, bypassing SQLAlchemy model validation
        result = db.execute(text("SELECT DISTINCT category FROM products"))
        print("Distinct categories in DB:")
        for row in result:
            print(f"'{row[0]}'")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_categories()
