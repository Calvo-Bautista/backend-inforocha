import sys
import os
from sqlalchemy import create_engine, text

# Add parent directory to path to import app modules if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine

def migrate_db():
    print(f"Connecting to database...")
    
    with engine.connect() as connection:
        # Check if invoice_type column exists
        try:
            print("Checking if invoice_type column exists...")
            result = connection.execute(text("SELECT invoice_type FROM orders LIMIT 1"))
            print("Column invoice_type already exists.")
        except Exception:
            print("Column invoice_type does not exist. Adding it...")
            # We need to commit the transaction if there was an error in some DBs, but SQLAlchemy handles it.
            # However, since the previous command failed, we might need to rollback current trans if inside one.
            # But engine.connect() usually starts one.
            # Let's just run the ALTER command.
            try:
                connection.execute(text("ALTER TABLE orders ADD COLUMN invoice_type VARCHAR(20)"))
                connection.commit()
                print("Column invoice_type added successfully.")
            except Exception as e:
                print(f"Error adding column: {e}")
                return

        # Check if factura_a column exists and drop it if desired, or keep it for safety.
        # The user seems to have issues, so let's check if it exists.
        try:
            print("Checking if factura_a column exists...")
            connection.execute(text("SELECT factura_a FROM orders LIMIT 1"))
            print("Column factura_a exists. Dropping it to avoid confusion...")
            try:
                connection.execute(text("ALTER TABLE orders DROP COLUMN factura_a"))
                connection.commit()
                print("Column factura_a dropped successfully.")
            except Exception as e:
                print(f"Error dropping column: {e}")
        except Exception:
            print("Column factura_a does not exist (already removed? or never existed).")

    print("Migration completed.")

if __name__ == "__main__":
    migrate_db()
