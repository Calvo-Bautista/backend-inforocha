"""
Quick test to verify database connection
"""
import sys
sys.path.append('.')

from app.core.config import settings
from sqlalchemy import create_engine, text

print(f"Testing database connection...")
print(f"Database URL: {settings.DATABASE_URL}")

try:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        print(f"Result: {result.fetchone()}")
except Exception as e:
    print(f"❌ Database connection failed!")
    print(f"Error: {e}")
    sys.exit(1)
