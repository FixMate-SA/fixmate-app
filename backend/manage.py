#!/usr/bin/env python3
"""
FixMate-SA Management Script for Heroku
Run admin commands on Heroku console with: python backend/manage.py <command>
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from database import get_db
from models import User, Fixer, Job, Review
from sqlalchemy.orm import Session
import uuid

def get_database_session():
    """Get database session."""
    try:
        db = next(get_db())
        return db
    except Exception as e:
        print(f"Database connection error: {e}")
        # Create tables if they don't exist
        from database import engine
        from models import Base
        Base.metadata.create_all(bind=engine)
        db = next(get_db())
        return db

def format_phone_number(phone: str) -> str:
    """Format phone number for database lookup."""
    # Remove any prefixes and standardize
    clean_phone = phone.replace('whatsapp:', '').replace(' ', '').replace('-', '')
    
    # Handle different formats
    if clean_phone.startswith('0') and len(clean_phone) == 10:
        return f"+27{clean_phone[1:]}"
    elif clean_phone.startswith('+27') and len(clean_phone) == 12:
        return clean_phone
    elif clean_phone.startswith('27') and len(clean_phone) == 11:
        return f"+{clean_phone}"
    else:
        # Try as-is for existing database formats
        return phone

def add_fixer(name, phone, skills, password=None):
    """Add a new fixer to the system with optional password."""
    try:
        db = get_database_session()
        formatted_phone = format_phone_number(phone)
        
        # Check if fixer already exists
        existing_fixer = db.query(Fixer).filter(Fixer.phone == formatted_phone).first()
        if existing_fixer:
            print(f"❌ Fixer with phone number {formatted_phone} already exists.")
            return
        
        # Create or get user
        user = db.query(User).filter(User.phone == formatted_phone).first()
        name_parts = name.split()
        first_name = name_parts[0] if name_parts else name
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        if not user:
            user = User(
                phone=formatted_phone,
                first_name=first_name,
                last_name=last_name,
                id_number=f"CLI_{uuid.uuid4().hex[:8]}",
                town="Unknown",
                role="fixer",
                is_active=True,
                is_verified=True  # Auto-verify CLI created fixers
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Created new user: {user.first_name} {user.last_name}")
        else:
            # Update existing user to fixer role
            user.role = "fixer"
            user.first_name = first_name
            user.last_name = last_name
            user.is_verified = True
            db.commit()
            print(f"✅ Updated existing user to fixer role: {user.first_name} {user.last_name}")
        
        # Set password if provided
        if password:
            import bcrypt
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            user.password_hash = hashed_password
            db.commit()
            print(f"✅ Password set for user: {password}")
        else:
            print(f"⚠️  No password set - user won't be able to login via web/app")
        
        # Create fixer record
        import json
        skills_list = [skill.strip() for skill in skills.split(',')]
        skills_json = json.dumps(skills_list)
        
        fixer = Fixer(
            user_id=user.id,
            phone=formatted_phone,
            name=name,
            email=f"{first_name.lower()}.{last_name.lower().replace(' ', '')}@fixmate.com",
            services=skills_json,
            location="Unknown",
            rating=5.0,  # Start with good rating
            total_jobs=0,
            is_active=True,
            is_approved=True,  # Auto-approve CLI created fixers
            availability_status="available"
        )
        
        db.add(fixer)
        db.commit()
        
        # Create fixer availability record for workflow system
        from models import FixerAvailability
        availability = FixerAvailability(
            fixer_id=fixer.id,
            is_available=True,
            has_outstanding_debt=False,
            debt_amount=0.0,
            is_suspended=False,
            completion_rate=100.0,
            reliability_score=100.0
        )
        db.add(availability)
        db.commit()
        
        print(f"✅ Successfully added fixer: '{name}' with phone {formatted_phone}")
        print(f"   Skills: {skills}")
        print(f"   Services JSON: {skills_json}")
        print(f"   Status: Approved and available for jobs")
        print(f"   Login: {formatted_phone} / {'***SET***' if password else 'NO PASSWORD'}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error adding fixer: {e}")

def add_fixer_with_password(name, phone, skills, password):
    """Add a new fixer to the system with password - enhanced version."""
    add_fixer(name, phone, skills, password)

def set_password(phone, password):
    """Set password for a user."""
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        db = get_database_session()
        formatted_phone = format_phone_number(phone)
        
        # Try different phone formats
        user = None
        phone_variations = [
            formatted_phone,
            f"whatsapp:{formatted_phone}",
            phone,
        ]
        
        for phone_var in phone_variations:
            user = db.query(User).filter(User.phone == phone_var).first()
            if user:
                break
        
        if not user:
            print(f"❌ User with phone number {phone} not found.")
            return
        
        # Hash and set password
        hashed_password = pwd_context.hash(password)
        user.password_hash = hashed_password
        db.commit()
        
        print(f"✅ Successfully set password for user: {user.first_name} {user.last_name} ({user.phone})")
        print(f"   Password: {password}")
        print(f"   Role: {user.role}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error setting password: {e}")

def promote_admin(phone):
    """Promote a user to admin status."""
    try:
        db = get_database_session()
        formatted_phone = format_phone_number(phone)
        
        # Try different phone formats to find user
        user = None
        phone_variations = [
            formatted_phone,
            f"whatsapp:{formatted_phone}",
            phone,  # original format
        ]
        
        for phone_var in phone_variations:
            user = db.query(User).filter(User.phone == phone_var).first()
            if user:
                break
        
        if not user:
            print(f"User not found with phone {phone}. Creating new admin user...")
            user = User(
                phone=formatted_phone,
                first_name="Admin",
                last_name="User", 
                id_number=f"CLI_{uuid.uuid4().hex[:8]}",
                town="Unknown",
                role="admin"
            )
            db.add(user)
            db.commit()
            print(f"✅ Successfully created and promoted new admin: {user.phone}")
        else:
            old_role = user.role
            user.role = "admin"
            db.commit()
            print(f"✅ Successfully promoted user '{user.first_name} {user.last_name}' from {old_role} to admin")
            
        db.close()
        
    except Exception as e:
        print(f"❌ Error promoting admin: {e}")

def demote_admin(phone):
    """Demote an admin to regular client status."""
    try:
        db = get_database_session()
        formatted_phone = format_phone_number(phone)
        
        # Try different phone formats
        user = None
        phone_variations = [
            formatted_phone,
            f"whatsapp:{formatted_phone}",
            phone,
        ]
        
        for phone_var in phone_variations:
            user = db.query(User).filter(User.phone == phone_var).first()
            if user:
                break
        
        if not user:
            print(f"❌ User with phone number {phone} not found.")
            return
        
        old_role = user.role
        user.role = "client"
        db.commit()
        print(f"✅ Successfully demoted '{user.first_name} {user.last_name}' from {old_role} to client")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error demoting admin: {e}")

def remove_fixer(phone):
    """Remove a fixer from the system."""
    try:
        db = get_database_session()
        formatted_phone = format_phone_number(phone)
        
        # Try different phone formats
        fixer = None
        phone_variations = [
            formatted_phone,
            f"whatsapp:{formatted_phone}",
            phone,
        ]
        
        for phone_var in phone_variations:
            fixer = db.query(Fixer).filter(Fixer.phone == phone_var).first()
            if fixer:
                break
        
        if not fixer:
            print(f"❌ Fixer with phone number {phone} not found.")
            return
        
        fixer_name = fixer.name
        fixer_phone = fixer.phone
        
        # Set as inactive instead of deleting to preserve data integrity
        fixer.is_active = False
        db.commit()
        print(f"✅ Successfully deactivated fixer: {fixer_name} ({fixer_phone})")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error removing fixer: {e}")

def remove_client(phone):
    """Remove a client from the system."""
    try:
        db = get_database_session()
        formatted_phone = format_phone_number(phone)
        
        # Try different phone formats
        user = None
        phone_variations = [
            formatted_phone,
            f"whatsapp:{formatted_phone}", 
            phone,
        ]
        
        for phone_var in phone_variations:
            user = db.query(User).filter(User.phone == phone_var).first()
            if user:
                break
        
        if not user:
            print(f"❌ Client with phone number {phone} not found.")
            return
        
        user_name = f"{user.first_name} {user.last_name}"
        user_phone = user.phone
        
        # Set as inactive instead of deleting
        user.is_active = False
        db.commit()
        print(f"✅ Successfully deactivated client: {user_name} ({user_phone})")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error removing client: {e}")

def reassign_job(job_id, new_fixer_phone):
    """Reassign a job to a different fixer."""
    try:
        db = get_database_session()
        
        # Find the job
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            print(f"❌ Job with ID {job_id} not found.")
            return
        
        # Find the new fixer
        formatted_phone = format_phone_number(new_fixer_phone)
        fixer = None
        phone_variations = [
            formatted_phone,
            f"whatsapp:{formatted_phone}",
            new_fixer_phone,
        ]
        
        for phone_var in phone_variations:
            fixer = db.query(Fixer).filter(Fixer.phone == phone_var, Fixer.is_active == True).first()
            if fixer:
                break
        
        if not fixer:
            print(f"❌ Active fixer with phone number {new_fixer_phone} not found.")
            return
        
        old_fixer_id = job.fixer_id
        job.fixer_id = fixer.id
        job.status = "assigned"
        db.commit()
        
        print(f"✅ Successfully reassigned job {job_id} to fixer {fixer.name} ({fixer.phone})")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error reassigning job: {e}")

def list_users():
    """List all users in the system."""
    try:
        db = get_database_session()
        users = db.query(User).all()
        
        print("\n📋 All Users:")
        print("-" * 80)
        print(f"{'Name':<20} {'Phone':<20} {'Role':<10} {'Active':<8} {'Town':<15}")
        print("-" * 80)
        
        for user in users:
            name = f"{user.first_name} {user.last_name}"
            print(f"{name:<20} {user.phone:<20} {user.role:<10} {'Yes' if user.is_active else 'No':<8} {user.town or 'Unknown':<15}")
        
        print(f"\nTotal: {len(users)} users")
        db.close()
        
    except Exception as e:
        print(f"❌ Error listing users: {e}")

def list_fixers():
    """List all fixers in the system."""
    try:
        db = get_database_session()
        fixers = db.query(Fixer).all()
        
        print("\n🔧 All Fixers:")
        print("-" * 80)
        print(f"{'Name':<20} {'Phone':<20} {'Location':<15} {'Rating':<8} {'Active':<8}")
        print("-" * 80)
        
        for fixer in fixers:
            print(f"{fixer.name:<20} {fixer.phone:<20} {fixer.location:<15} {fixer.rating:<8.1f} {'Yes' if fixer.is_active else 'No':<8}")
        
        print(f"\nTotal: {len(fixers)} fixers")
        db.close()
        
    except Exception as e:
        print(f"❌ Error listing fixers: {e}")

def stats():
    """Show system statistics."""
    try:
        db = get_database_session()
        
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        admins = db.query(User).filter(User.role == "admin").count()
        clients = db.query(User).filter(User.role == "client").count()
        
        total_fixers = db.query(Fixer).count()
        active_fixers = db.query(Fixer).filter(Fixer.is_active == True).count()
        
        total_jobs = db.query(Job).count()
        completed_jobs = db.query(Job).filter(Job.status == "completed").count()
        
        total_reviews = db.query(Review).count()
        
        print("\n📊 FixMate-SA System Statistics:")
        print("=" * 50)
        print(f"Users:           {total_users} total ({active_users} active)")
        print(f"  - Admins:      {admins}")
        print(f"  - Clients:     {clients}")
        print(f"Fixers:          {total_fixers} total ({active_fixers} active)")
        print(f"Jobs:            {total_jobs} total ({completed_jobs} completed)")
        print(f"Reviews:         {total_reviews}")
        print("=" * 50)
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")

def migrate():
    """Run database migration - equivalent to flask db upgrade"""
    try:
        from migrate_db import main as migrate_main
        print("🚀 Running FixMate database migration...")
        return migrate_main()
    except ImportError:
        print("❌ Migration module not found")
        return 1

def check_db():
    """Check database connection and table status"""
    try:
        from database import engine
        from sqlalchemy import text
        
        print("🔍 Checking database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            
            # Check workflow tables
            workflow_tables = [
                'users', 'fixers', 'jobs', 'platform_terms', 
                'fixer_availability', 'job_assignment_history'
            ]
            
            existing_tables = []
            missing_tables = []
            
            for table in workflow_tables:
                try:
                    conn.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                    existing_tables.append(table)
                except:
                    missing_tables.append(table)
            
            print(f"✅ Found {len(existing_tables)} core tables")
            if missing_tables:
                print(f"⚠️  Missing tables: {', '.join(missing_tables)}")
                print("💡 Run 'python backend/manage.py migrate' to create missing tables")
            
        return 0
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return 1

def show_help():
    """Show available commands."""
    print("\n🛠️  FixMate-SA Management Commands")
    print("=" * 50)
    print("Database Management:")
    print("  migrate                        - Run database migration (like flask db upgrade)")
    print("  check-db                       - Check database connection and tables")
    print("")
    print("Fixer Management:")
    print("  add-fixer <name> <phone> <skills> [password]     - Add a new fixer (optionally with password)")
    print("  add-fixer-pwd <name> <phone> <skills> <password> - Add a new fixer with password (required)")
    print("  remove-fixer <phone>                            - Deactivate a fixer")
    print("")
    print("User Management:")
    print("  promote-admin <phone>          - Promote user to admin")
    print("  demote-admin <phone>           - Demote admin to client")
    print("  remove-client <phone>          - Deactivate a client")
    print("  set-password <phone> <password> - Set password for user")
    print("")
    print("Job Management:")
    print("  reassign-job <job_id> <phone>  - Reassign job to different fixer")
    print("")
    print("Information:")
    print("  list-users                     - List all users")
    print("  list-fixers                    - List all fixers")
    print("  stats                          - Show system statistics")
    print("  help                           - Show this help message")
    print("")
    print("Heroku Usage Examples:")
    print("  heroku run python backend/manage.py migrate")
    print("  heroku run python backend/manage.py check-db")
    print("  heroku run python backend/manage.py add-fixer \"John Smith\" 0791135003 \"plumbing,electrical\"")
    print("  heroku run python backend/manage.py add-fixer-pwd \"John Smith\" 0791135003 \"plumbing,electrical\" fixer123")
    print("  heroku run python backend/manage.py set-password 0821111111 fixer123")
    print("  heroku run python backend/manage.py promote-admin 0791135003")
    print("=" * 50)

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "migrate":
        migrate()
    
    elif command == "check-db":
        check_db()
    
    elif command == "add-fixer":
        if len(sys.argv) < 5 or len(sys.argv) > 6:
            print("❌ Usage: python backend/manage.py add-fixer \"Full Name\" \"phone\" \"skill1,skill2,skill3\" [password]")
            print("   Example: python backend/manage.py add-fixer \"John Smith\" \"0791135003\" \"plumbing,electrical\"")
            print("   With password: python backend/manage.py add-fixer \"John Smith\" \"0791135003\" \"plumbing,electrical\" fixer123")
            return
        password = sys.argv[5] if len(sys.argv) == 6 else None
        add_fixer(sys.argv[2], sys.argv[3], sys.argv[4], password)
    
    elif command == "add-fixer-pwd":
        if len(sys.argv) != 6:
            print("❌ Usage: python backend/manage.py add-fixer-pwd \"Full Name\" \"phone\" \"skill1,skill2,skill3\" \"password\"")
            print("   Example: python backend/manage.py add-fixer-pwd \"John Smith\" \"0791135003\" \"plumbing,electrical\" fixer123")
            return
        add_fixer_with_password(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    
    elif command == "set-password":
        if len(sys.argv) != 4:
            print("❌ Usage: python backend/manage.py set-password <phone> <password>")
            return
        set_password(sys.argv[2], sys.argv[3])
    
    elif command == "promote-admin":
        if len(sys.argv) != 3:
            print("❌ Usage: python backend/manage.py promote-admin <phone>")
            return
        promote_admin(sys.argv[2])
    
    elif command == "demote-admin":
        if len(sys.argv) != 3:
            print("❌ Usage: python backend/manage.py demote-admin <phone>")
            return
        demote_admin(sys.argv[2])
    
    elif command == "remove-fixer":
        if len(sys.argv) != 3:
            print("❌ Usage: python backend/manage.py remove-fixer <phone>")
            return
        remove_fixer(sys.argv[2])
    
    elif command == "remove-client":
        if len(sys.argv) != 3:
            print("❌ Usage: python backend/manage.py remove-client <phone>")
            return
        remove_client(sys.argv[2])
    
    elif command == "reassign-job":
        if len(sys.argv) != 4:
            print("❌ Usage: python backend/manage.py reassign-job <job_id> <new_fixer_phone>")
            return
        reassign_job(sys.argv[2], sys.argv[3])
    
    elif command == "list-users":
        list_users()
    
    elif command == "list-fixers":
        list_fixers()
    
    elif command == "stats":
        stats()
    
    elif command == "help":
        show_help()
    
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()