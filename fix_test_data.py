#!/usr/bin/env python3
"""
Fix test data for Automatic Job Allocation System
Creates fixer profile and approves fixers using direct SQL
"""

import os
import sys
sys.path.append('/app/backend')

from database import get_db
from sqlalchemy import text
import uuid

def fix_test_data():
    """Fix test data for job allocation testing"""
    print("🔧 Fixing test data for Automatic Job Allocation System...")
    
    db = next(get_db())
    
    try:
        # 1. Create fixer profile for test user c417ef19-cdb6-44ee-80aa-8128e0ff8e75
        fixer_user_id = "c417ef19-cdb6-44ee-80aa-8128e0ff8e75"
        fixer_id = f"fixer_{uuid.uuid4()}"
        
        # Check if fixer profile already exists
        check_query = text("SELECT id FROM fixers WHERE user_id = :user_id")
        existing = db.execute(check_query, {'user_id': fixer_user_id}).fetchone()
        
        if not existing:
            print(f"Creating fixer profile for user: {fixer_user_id}")
            
            insert_fixer_query = text("""
                INSERT INTO fixers (
                    id, user_id, phone, name, email, services, location, rating, 
                    total_jobs, is_active, is_approved, jobs_completed, 
                    completion_percentage, skills, created_at
                ) VALUES (
                    :id, :user_id, :phone, :name, :email, :services, :location, :rating,
                    :total_jobs, :is_active, :is_approved, :jobs_completed,
                    :completion_percentage, :skills, :created_at
                )
            """)
            
            from datetime import datetime
            import json
            
            db.execute(insert_fixer_query, {
                'id': fixer_id,
                'user_id': fixer_user_id,
                'phone': 'whatsapp:+27800000003',  # Add phone number
                'name': 'Test Fixer User',
                'email': 'testfixer@fixmate.test',
                'services': json.dumps(["Electrical", "Plumbing", "Handyman"]),
                'location': 'Cape Town, South Africa',
                'rating': 4.5,
                'total_jobs': 0,
                'is_active': True,
                'is_approved': True,  # Approve immediately
                'jobs_completed': 0,
                'completion_percentage': 100.0,
                'skills': json.dumps(["electrical_repair", "plumbing_installation", "general_maintenance"]),
                'created_at': datetime.utcnow()
            })
            
            print("✅ Created fixer profile for test user")
        else:
            print("✅ Fixer profile already exists for test user")
            
            # Update to ensure it's approved
            update_query = text("UPDATE fixers SET is_approved = true WHERE user_id = :user_id")
            db.execute(update_query, {'user_id': fixer_user_id})
            print("✅ Ensured fixer profile is approved")
        
        # 2. Approve at least one existing fixer with Electrical service
        print("Approving existing fixers with Electrical service...")
        
        approve_query = text("""
            UPDATE fixers 
            SET is_approved = true 
            WHERE is_active = true 
            AND (services ILIKE '%Electrical%' OR services ILIKE '%electrical%')
            AND is_approved = false
        """)
        
        result = db.execute(approve_query)
        approved_count = result.rowcount
        
        print(f"✅ Approved {approved_count} existing fixers with Electrical service")
        
        # 3. Verify the changes
        print("\nVerifying changes...")
        
        # Check approved fixers with Electrical service
        verify_query = text("""
            SELECT id, name, services, is_approved 
            FROM fixers 
            WHERE is_active = true 
            AND is_approved = true
            AND (services ILIKE '%Electrical%' OR services ILIKE '%electrical%')
        """)
        
        approved_fixers = db.execute(verify_query).fetchall()
        print(f"✅ Found {len(approved_fixers)} approved fixers with Electrical service:")
        
        for fixer in approved_fixers:
            print(f"   - {fixer[1]} (ID: {fixer[0]})")
        
        # Check our test user's fixer profile
        test_fixer_query = text("""
            SELECT id, name, is_approved, services 
            FROM fixers 
            WHERE user_id = :user_id
        """)
        
        test_fixer = db.execute(test_fixer_query, {'user_id': fixer_user_id}).fetchone()
        
        if test_fixer:
            print(f"✅ Test user fixer profile: {test_fixer[1]} (Approved: {test_fixer[2]})")
        else:
            print("❌ Test user fixer profile not found")
        
        db.commit()
        print("\n🎉 Test data setup complete!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_test_data()