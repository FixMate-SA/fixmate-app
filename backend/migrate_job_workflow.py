#!/usr/bin/env python3
"""
Database migration for complete job workflow system
Adds fields for:
- Job completion with images (before/after)
- Fixer ratings and reviews
- Money spent tracking for clients
- Total earned tracking for fixers
- Job notifications
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from database import get_db
from models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Run the migration to add new job workflow fields"""
    
    # Get database engine
    engine = create_engine(os.environ.get('MONGO_URL', 'sqlite:///fixmate.db'))
    
    logger.info("Starting job workflow database migration...")
    
    try:
        with engine.connect() as connection:
            # Add new fields to users table
            logger.info("Adding money_spent field to users table...")
            try:
                connection.execute(text("ALTER TABLE users ADD COLUMN money_spent REAL DEFAULT 0.0"))
                logger.info("✅ Added money_spent to users")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("⚠️  money_spent column already exists in users table")
                else:
                    logger.error(f"❌ Error adding money_spent to users: {e}")
            
            # Add new fields to fixers table
            logger.info("Adding total_earned field to fixers table...")
            try:
                connection.execute(text("ALTER TABLE fixers ADD COLUMN total_earned REAL DEFAULT 0.0"))
                logger.info("✅ Added total_earned to fixers")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("⚠️  total_earned column already exists in fixers table")
                else:
                    logger.error(f"❌ Error adding total_earned to fixers: {e}")
            
            # Add new fields to jobs table
            job_fields = [
                ("assigned_fixer_id", "TEXT"),
                ("before_image", "TEXT"),
                ("after_image", "TEXT"),
                ("fixer_rating", "INTEGER"),
                ("fixer_review", "TEXT"),
                ("rated_at", "TIMESTAMP"),
                ("completed_at", "TIMESTAMP"),
                ("accepted_at", "TIMESTAMP")
            ]
            
            for field_name, field_type in job_fields:
                logger.info(f"Adding {field_name} field to jobs table...")
                try:
                    connection.execute(text(f"ALTER TABLE jobs ADD COLUMN {field_name} {field_type}"))
                    logger.info(f"✅ Added {field_name} to jobs")
                except Exception as e:
                    if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                        logger.info(f"⚠️  {field_name} column already exists in jobs table")
                    else:
                        logger.error(f"❌ Error adding {field_name} to jobs: {e}")
            
            # Add job_id field to fixer_payments table
            logger.info("Adding job_id field to fixer_payments table...")
            try:
                connection.execute(text("ALTER TABLE fixer_payments ADD COLUMN job_id TEXT"))
                logger.info("✅ Added job_id to fixer_payments")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("⚠️  job_id column already exists in fixer_payments table")
                else:
                    logger.error(f"❌ Error adding job_id to fixer_payments: {e}")
            
            # Create notifications table
            logger.info("Creating notifications table...")
            try:
                connection.execute(text("""
                    CREATE TABLE notifications (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        message TEXT NOT NULL,
                        job_id TEXT,
                        read BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (job_id) REFERENCES jobs (id)
                    )
                """))
                logger.info("✅ Created notifications table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("⚠️  notifications table already exists")
                else:
                    logger.error(f"❌ Error creating notifications table: {e}")
            
            connection.commit()
            logger.info("🎉 Job workflow migration completed successfully!")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise
    
    # Create all missing tables
    logger.info("Creating any missing tables...")
    try:
        Base.metadata.create_all(engine)
        logger.info("✅ All tables verified/created")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    run_migration()
    print("Migration completed!")