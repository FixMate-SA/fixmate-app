#!/usr/bin/env python3
"""
Add profile enhancement fields to users table
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def add_profile_fields():
    """Add new profile fields to users table"""
    
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
            # Add new columns to users table for enhanced profiles
            new_columns = [
                # Basic profile fields
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_image TEXT',
                
                # Fixer-specific fields
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS services TEXT',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS experience_years INTEGER',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS hourly_rate DECIMAL(10,2)',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS availability_status VARCHAR(50) DEFAULT \'available\'',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS service_area TEXT',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS certifications TEXT',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS portfolio_images TEXT',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS rating DECIMAL(3,2) DEFAULT 5.0',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS total_jobs INTEGER DEFAULT 0',
                
                # Admin-specific fields
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS admin_level VARCHAR(50) DEFAULT \'standard\'',
                'ALTER TABLE users ADD COLUMN IF NOT EXISTS department VARCHAR(100) DEFAULT \'general\'',
            ]
            
            print("🔧 Adding profile enhancement fields to users table...")
            
            for query in new_columns:
                try:
                    connection.execute(text(query))
                    field_name = query.split('ADD COLUMN IF NOT EXISTS')[1].split()[0]
                    print(f"✅ Added field: {field_name}")
                except Exception as e:
                    field_name = query.split('ADD COLUMN IF NOT EXISTS')[1].split()[0] if 'ADD COLUMN' in query else 'unknown'
                    print(f"⚠️ Field {field_name} may already exist or error occurred: {e}")
            
            connection.commit()
            
            # Verify new columns were added
            verify_query = text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN (
                    'profile_image', 'services', 'experience_years', 'hourly_rate',
                    'availability_status', 'service_area', 'certifications', 
                    'portfolio_images', 'rating', 'total_jobs', 'admin_level', 'department'
                )
                ORDER BY column_name;
            """)
            
            result = connection.execute(verify_query)
            columns = result.fetchall()
            
            print(f"\n📊 Verified {len(columns)} new profile fields:")
            for column in columns:
                print(f"   - {column[0]}: {column[1]} {'NULL' if column[2] == 'YES' else 'NOT NULL'}")
            
            print("\n✅ Profile enhancement fields added successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error adding profile fields: {e}")
        return False

if __name__ == "__main__":
    success = add_profile_fields()
    sys.exit(0 if success else 1)