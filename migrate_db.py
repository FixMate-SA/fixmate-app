#!/usr/bin/env python3
"""
Database migration script to add payment system tables and columns
"""

import os
import sys
sys.path.append('/app/backend')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def migrate_database():
    """Add payment system tables and columns"""
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            print("Starting database migration...")
            
            # Add payment_status column to fixers table if it doesn't exist
            print("Adding payment_status column to fixers table...")
            conn.execute(text("""
                ALTER TABLE fixers 
                ADD COLUMN IF NOT EXISTS payment_status VARCHAR DEFAULT 'current'
            """))
            
            # Create fixer_payments table
            print("Creating fixer_payments table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS fixer_payments (
                    id VARCHAR PRIMARY KEY,
                    fixer_id VARCHAR NOT NULL REFERENCES fixers(id),
                    amount FLOAT NOT NULL,
                    payment_type VARCHAR NOT NULL,
                    payment_method VARCHAR,
                    payment_reference VARCHAR,
                    status VARCHAR DEFAULT 'pending',
                    description TEXT,
                    due_date TIMESTAMP NOT NULL,
                    paid_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create fixer_verifications table
            print("Creating fixer_verifications table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS fixer_verifications (
                    id VARCHAR PRIMARY KEY,
                    fixer_id VARCHAR NOT NULL REFERENCES fixers(id),
                    id_document_url VARCHAR,
                    verification_status VARCHAR DEFAULT 'pending',
                    admin_notes TEXT,
                    verified_by VARCHAR,
                    verified_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Commit transaction
            trans.commit()
            print("Database migration completed successfully!")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    migrate_database()