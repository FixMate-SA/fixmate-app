#!/usr/bin/env python3
"""
Migration script to create announcement system tables
This script creates the necessary tables for the new announcement and chat system.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variables"""
    # Check for MONGO_URL first (for consistency with existing code)
    db_url = os.environ.get('MONGO_URL')
    if not db_url:
        # Fallback to DATABASE_URL 
        db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        logger.error("No database URL found. Set MONGO_URL or DATABASE_URL environment variable.")
        return None
    
    # Handle PostgreSQL URL format for newer drivers
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    return db_url

def create_announcement_tables():
    """Create announcement system tables"""
    db_url = get_database_url()
    if not db_url:
        return False
    
    try:
        logger.info(f"Connecting to database...")
        engine = create_engine(db_url)
        
        # Create announcements table
        announcements_sql = '''
        CREATE TABLE IF NOT EXISTS announcements (
            id VARCHAR PRIMARY KEY,
            title VARCHAR NOT NULL,
            content TEXT NOT NULL,
            target_audience VARCHAR NOT NULL,
            created_by VARCHAR NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            is_pinned BOOLEAN DEFAULT FALSE,
            priority VARCHAR DEFAULT 'normal',
            chat_enabled BOOLEAN DEFAULT TRUE,
            admin_only_chat BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );
        '''
        
        # Create announcement_chats table
        announcement_chats_sql = '''
        CREATE TABLE IF NOT EXISTS announcement_chats (
            id VARCHAR PRIMARY KEY,
            announcement_id VARCHAR NOT NULL,
            user_id VARCHAR NOT NULL,
            message TEXT NOT NULL,
            message_type VARCHAR DEFAULT 'user',
            is_admin_message BOOLEAN DEFAULT FALSE,
            is_deleted BOOLEAN DEFAULT FALSE,
            is_edited BOOLEAN DEFAULT FALSE,
            edited_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (announcement_id) REFERENCES announcements(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        '''
        
        # Create indexes for better performance
        indexes_sql = '''
        CREATE INDEX IF NOT EXISTS idx_announcements_target_audience ON announcements(target_audience);
        CREATE INDEX IF NOT EXISTS idx_announcements_is_active ON announcements(is_active);
        CREATE INDEX IF NOT EXISTS idx_announcements_created_at ON announcements(created_at);
        CREATE INDEX IF NOT EXISTS idx_announcement_chats_announcement_id ON announcement_chats(announcement_id);
        CREATE INDEX IF NOT EXISTS idx_announcement_chats_user_id ON announcement_chats(user_id);
        CREATE INDEX IF NOT EXISTS idx_announcement_chats_created_at ON announcement_chats(created_at);
        '''
        
        with engine.connect() as connection:
            logger.info("Creating announcements table...")
            connection.execute(text(announcements_sql))
            
            logger.info("Creating announcement_chats table...")
            connection.execute(text(announcement_chats_sql))
            
            logger.info("Creating indexes...")
            connection.execute(text(indexes_sql))
            
            connection.commit()
            
        logger.info("✅ Announcement system tables created successfully!")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error creating announcement tables: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error creating announcement tables: {e}")
        return False

def verify_tables():
    """Verify that the tables were created successfully"""
    db_url = get_database_url()
    if not db_url:
        return False
    
    try:
        engine = create_engine(db_url)
        
        with engine.connect() as connection:
            # Check announcements table
            result = connection.execute(text("SELECT 1 FROM announcements LIMIT 1;"))
            logger.info("✅ Announcements table verified")
            
            # Check announcement_chats table
            result = connection.execute(text("SELECT 1 FROM announcement_chats LIMIT 1;"))
            logger.info("✅ Announcement chats table verified")
            
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Error verifying tables: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error verifying tables: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting announcement system table creation...")
    
    if create_announcement_tables():
        logger.info("📊 Verifying tables...")
        if verify_tables():
            logger.info("🎉 Announcement system setup completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Table verification failed")
            sys.exit(1)
    else:
        logger.error("❌ Failed to create announcement system tables")
        sys.exit(1)