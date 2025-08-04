#!/usr/bin/env python3
"""
Database migration and table creation script
"""

import sys
import os
sys.path.append('/app/backend')

from database import engine, drop_and_recreate_tables
from models import Base

def main():
    print("🔧 Database Migration and Table Creation")
    print("=" * 50)
    
    try:
        print("📋 Creating all database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Test database connection
        from database import SessionLocal
        db = SessionLocal()
        try:
            # Try a simple query
            result = db.execute("SELECT 1")
            print("✅ Database connection test successful")
        except Exception as e:
            print(f"❌ Database connection test failed: {str(e)}")
        finally:
            db.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)