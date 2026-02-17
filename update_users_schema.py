
import sys
import os
from sqlalchemy import text

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine

def update_schema():
    print("Updating users table schema...")
    with engine.connect() as connection:
        # Check if columns exist (rudimentary check using try/except logic or information_schema if strict, 
        # but here we can try to add and ignore if exists or check information_schema)
        
        # Using raw SQL to be backend-agnostic enough for this setup (MySQL/MariaDB/Postgres usually support ALTER TABLE ADD COLUMN)
        # We are likely on MySQL based on previous errors (pymysql)
        
        try:
            print("Adding is_on_leave column...")
            connection.execute(text("ALTER TABLE users ADD COLUMN is_on_leave BOOLEAN DEFAULT FALSE"))
            print("Added is_on_leave.")
        except Exception as e:
            print(f"Skipping is_on_leave (might exist): {e}")

        try:
            print("Adding substitute_id column...")
            connection.execute(text("ALTER TABLE users ADD COLUMN substitute_id INTEGER NULL"))
            print("Added substitute_id.")
        except Exception as e:
            print(f"Skipping substitute_id (might exist): {e}")

        try:
            print("Adding Foreign Key for substitute_id...")
            connection.execute(text("ALTER TABLE users ADD CONSTRAINT fk_users_substitute FOREIGN KEY (substitute_id) REFERENCES users(id)"))
            print("Added Foreign Key.")
        except Exception as e:
             print(f"Skipping FK (might exist): {e}")

        connection.commit()
    print("Schema update script finished.")

if __name__ == "__main__":
    update_schema()
