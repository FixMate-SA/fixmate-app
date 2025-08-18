#!/usr/bin/env python3
"""
Create push notification related database tables
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_push_notification_tables():
    """Create push notification tables in the database"""
    
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if database_url and database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        if not database_url:
            print("❌ DATABASE_URL not found in environment variables")
            return False
        
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Create push_subscriptions table
            create_push_subscriptions_table = text("""
                CREATE TABLE IF NOT EXISTS push_subscriptions (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    user_role VARCHAR(50),
                    endpoint TEXT NOT NULL,
                    p256dh_key TEXT,
                    auth_key TEXT,
                    subscription_data TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_user_endpoint UNIQUE(user_id, endpoint),
                    CONSTRAINT fk_push_subscription_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
            """)
            
            # Create indexes for better performance
            create_indexes = text("""
                CREATE INDEX IF NOT EXISTS idx_push_subscriptions_user_id ON push_subscriptions(user_id);
                CREATE INDEX IF NOT EXISTS idx_push_subscriptions_user_role ON push_subscriptions(user_role);
                CREATE INDEX IF NOT EXISTS idx_push_subscriptions_is_active ON push_subscriptions(is_active);
                CREATE INDEX IF NOT EXISTS idx_push_subscriptions_created_at ON push_subscriptions(created_at);
            """)
            
            # Execute table creation
            connection.execute(create_push_subscriptions_table)
            connection.execute(create_indexes)
            connection.commit()
            
            print("✅ Push notification tables created successfully!")
            print("📊 Tables created:")
            print("   - push_subscriptions (with indexes)")
            
            # Verify table structure
            verify_query = text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'push_subscriptions'
                ORDER BY ordinal_position;
            """)
            
            result = connection.execute(verify_query)
            columns = result.fetchall()
            
            if columns:
                print("\n📋 Push subscriptions table structure:")
                for column in columns:
                    print(f"   - {column[0]}: {column[1]} {'NULL' if column[2] == 'YES' else 'NOT NULL'}")
            else:
                print("⚠️ Could not verify table structure")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating push notification tables: {e}")
        return False

if __name__ == "__main__":
    success = create_push_notification_tables()
    sys.exit(0 if success else 1)