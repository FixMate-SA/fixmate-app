#!/usr/bin/env python3
"""
Create WhatsApp Statistics Table Migration
Creates the whatsapp_statistics table for tracking real-time messaging data.
"""

import os
import sys
sys.path.append('/app/backend')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, WhatsAppStatistic
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_whatsapp_statistics_table():
    """Create the WhatsApp statistics table"""
    try:
        # Get database URL from environment
        database_url = os.getenv('MONGO_URL')
        if not database_url:
            logger.error("❌ MONGO_URL environment variable not set")
            return False
            
        logger.info("🚀 Creating WhatsApp statistics table...")
        
        # Create engine and session
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create the table
        with engine.begin() as connection:
            # Drop table if exists (for clean recreation)
            connection.execute(text("DROP TABLE IF EXISTS whatsapp_statistics;"))
            logger.info("📝 Dropped existing whatsapp_statistics table if it existed")
            
            # Create the table using SQLAlchemy
            WhatsAppStatistic.__table__.create(engine, checkfirst=True)
            logger.info("✅ Created whatsapp_statistics table successfully")
            
            # Verify table creation
            result = connection.execute(text("SELECT COUNT(*) FROM whatsapp_statistics;"))
            count = result.scalar()
            logger.info(f"📊 WhatsApp statistics table created with {count} records")
            
        logger.info("🎉 WhatsApp statistics table migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating WhatsApp statistics table: {str(e)}")
        return False

def create_indexes():
    """Create indexes for better performance"""
    try:
        database_url = os.getenv('MONGO_URL')
        engine = create_engine(database_url)
        
        with engine.begin() as connection:
            # Create performance indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_whatsapp_stats_created_at ON whatsapp_statistics(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_whatsapp_stats_event_type ON whatsapp_statistics(event_type);",
                "CREATE INDEX IF NOT EXISTS idx_whatsapp_stats_service_detected ON whatsapp_statistics(service_detected);",
                "CREATE INDEX IF NOT EXISTS idx_whatsapp_stats_conversation_id ON whatsapp_statistics(conversation_id);",
                "CREATE INDEX IF NOT EXISTS idx_whatsapp_stats_phone_number ON whatsapp_statistics(phone_number);"
            ]
            
            for index_sql in indexes:
                connection.execute(text(index_sql))
                
            logger.info("✅ Created performance indexes for WhatsApp statistics")
            
    except Exception as e:
        logger.error(f"❌ Error creating indexes: {str(e)}")

if __name__ == "__main__":
    logger.info("🔧 WhatsApp Statistics Table Migration Starting...")
    
    if create_whatsapp_statistics_table():
        create_indexes()
        logger.info("🎉 WhatsApp statistics system ready for real-time tracking!")
    else:
        logger.error("❌ Migration failed - WhatsApp statistics not available")
        sys.exit(1)