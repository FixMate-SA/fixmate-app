#!/usr/bin/env python3
"""
Database migration for password reset system
Adds password_reset_code and password_reset_expires fields to users table
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Run the migration to add password reset fields"""
    
    # Get database URL and fix the dialect
    db_url = os.environ.get('MONGO_URL', 'sqlite:///fixmate.db')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    # Get database engine
    engine = create_engine(db_url)
    
    logger.info("Starting password reset database migration...")
    
    try:
        with engine.connect() as connection:
            # Add password reset fields to users table
            reset_fields = [
                ("password_reset_code", "TEXT"),
                ("password_reset_expires", "TIMESTAMP")
            ]
            
            for field_name, field_type in reset_fields:
                logger.info(f"Adding {field_name} field to users table...")
                try:
                    connection.execute(text(f"ALTER TABLE users ADD COLUMN {field_name} {field_type}"))
                    logger.info(f"✅ Added {field_name} to users")
                except Exception as e:
                    if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                        logger.info(f"⚠️  {field_name} column already exists in users table")
                    else:
                        logger.error(f"❌ Error adding {field_name} to users: {e}")
            
            connection.commit()
            logger.info("🎉 Password reset migration completed successfully!")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()
    print("Password reset migration completed!")