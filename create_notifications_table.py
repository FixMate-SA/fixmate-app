#!/usr/bin/env python3
"""
Create fixer_notifications table for the job allocation system
"""

import os
import sys
sys.path.append('/app/backend')

from database import get_db
from sqlalchemy import text

def create_notifications_table():
    """Create the fixer_notifications table"""
    print("🔧 Creating fixer_notifications table...")
    
    db = next(get_db())
    
    try:
        # Create the fixer_notifications table
        create_table_query = text("""
            CREATE TABLE IF NOT EXISTS fixer_notifications (
                id VARCHAR PRIMARY KEY,
                fixer_id VARCHAR NOT NULL,
                job_id VARCHAR NOT NULL,
                notification_type VARCHAR DEFAULT 'job_assigned',
                title VARCHAR NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        db.execute(create_table_query)
        db.commit()
        
        print("✅ fixer_notifications table created successfully")
        
        # Verify the table exists
        verify_query = text("SELECT COUNT(*) FROM fixer_notifications")
        result = db.execute(verify_query).fetchone()
        
        print(f"✅ Table verified - contains {result[0]} notifications")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_notifications_table()