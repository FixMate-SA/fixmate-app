#!/usr/bin/env python3
"""
FixMate-SA Database Migration Script
Equivalent to 'flask db upgrade' for FastAPI applications
Safe to run multiple times (idempotent) and works on Heroku
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, ProgrammingError

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our models and database setup
from models import (
    Base, User, Fixer, Job, Review, 
    JobAssignmentHistory, JobNotification, FixerAvailability, 
    FixerBehaviorAnalysis, PlatformTerms, UserTermsAcceptance,
    FixerApplication, FixerVerification, FixerPayment,
    BusinessComplianceRequest, EmergencyAlert
)
from database import engine

class DatabaseMigrator:
    def __init__(self):
        self.engine = engine
        self.inspector = inspect(self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.db = SessionLocal()
        
    def log(self, message, level="INFO"):
        """Log migration messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def table_exists(self, table_name):
        """Check if a table exists"""
        return self.inspector.has_table(table_name)
    
    def column_exists(self, table_name, column_name):
        """Check if a column exists in a table"""
        if not self.table_exists(table_name):
            return False
        columns = [col['name'] for col in self.inspector.get_columns(table_name)]
        return column_name in columns
    
    def add_column_if_not_exists(self, table_name, column_name, column_definition):
        """Add a column to a table if it doesn't exist"""
        if not self.column_exists(table_name, column_name):
            try:
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
                self.db.execute(text(sql))
                self.db.commit()
                self.log(f"✅ Added column '{column_name}' to table '{table_name}'")
                return True
            except Exception as e:
                self.log(f"❌ Error adding column '{column_name}' to '{table_name}': {str(e)}", "ERROR")
                self.db.rollback()
                return False
        else:
            self.log(f"ℹ️  Column '{column_name}' already exists in table '{table_name}'")
            return True
    
    def create_table_if_not_exists(self, table_name, model_class):
        """Create a table if it doesn't exist"""
        if not self.table_exists(table_name):
            try:
                model_class.__table__.create(bind=self.engine, checkfirst=True)
                self.log(f"✅ Created table '{table_name}'")
                return True
            except Exception as e:
                self.log(f"❌ Error creating table '{table_name}': {str(e)}", "ERROR")
                return False
        else:
            self.log(f"ℹ️  Table '{table_name}' already exists")
            return True
    
    def migrate_workflow_system(self):
        """Migrate the workflow system changes"""
        self.log("🚀 Starting FixMate Workflow System Migration")
        
        success_count = 0
        total_steps = 0
        
        # Step 1: Create new workflow tables
        workflow_tables = [
            ('job_assignment_history', JobAssignmentHistory),
            ('job_notifications', JobNotification),
            ('fixer_availability', FixerAvailability),
            ('fixer_behavior_analysis', FixerBehaviorAnalysis),
            ('platform_terms', PlatformTerms),
            ('user_terms_acceptance', UserTermsAcceptance)
        ]
        
        self.log("📋 Creating new workflow tables...")
        for table_name, model_class in workflow_tables:
            total_steps += 1
            if self.create_table_if_not_exists(table_name, model_class):
                success_count += 1
        
        # Step 2: Add workflow columns to existing jobs table
        self.log("🔧 Adding workflow columns to jobs table...")
        job_workflow_columns = [
            ('terms_accepted', 'BOOLEAN DEFAULT FALSE'),
            ('terms_accepted_at', 'TIMESTAMP'),
            ('workflow_stage', 'VARCHAR DEFAULT \'pending\''),
            ('notified_fixers', 'TEXT'),
            ('eligible_fixers', 'TEXT'),
            ('assignment_timeout', 'TIMESTAMP'),
            ('attendance_timeout', 'TIMESTAMP'),
            ('is_emergency_escalated', 'BOOLEAN DEFAULT FALSE'),
            ('priority_level', 'VARCHAR DEFAULT \'normal\''),
            ('fixer_location_lat', 'FLOAT'),
            ('fixer_location_lng', 'FLOAT'),
            ('fixer_location_updated', 'TIMESTAMP'),
            ('estimated_arrival', 'TIMESTAMP'),
            ('tracking_active', 'BOOLEAN DEFAULT FALSE'),
            ('assignment_attempts', 'INTEGER DEFAULT 0'),
            ('last_assignment_attempt', 'TIMESTAMP'),
            ('auto_reassignment_count', 'INTEGER DEFAULT 0')
        ]
        
        for column_name, column_def in job_workflow_columns:
            total_steps += 1
            if self.add_column_if_not_exists('jobs', column_name, column_def):
                success_count += 1
        
        # Step 3: Create default platform terms if not exist
        total_steps += 1
        if self.create_default_terms():
            success_count += 1
        
        # Step 4: Initialize fixer availability records
        total_steps += 1
        if self.initialize_fixer_availability():
            success_count += 1
        
        # Step 5: Update existing jobs with workflow defaults
        total_steps += 1
        if self.update_existing_jobs():
            success_count += 1
        
        # Migration summary
        self.log(f"🎉 Migration completed: {success_count}/{total_steps} steps successful")
        
        if success_count == total_steps:
            self.log("✅ All workflow system features are now active!")
            return True
        else:
            self.log(f"⚠️  Migration completed with {total_steps - success_count} warnings/errors")
            return False
    
    def create_default_terms(self):
        """Create default platform terms if they don't exist"""
        try:
            # Check if any terms exist
            existing_terms = self.db.query(PlatformTerms).first()
            if existing_terms:
                self.log("ℹ️  Platform terms already exist")
                return True
            
            default_terms = PlatformTerms(
                version="1.0",
                title="FixMate-SA Platform Terms and Conditions",
                content="""
FixMate-SA Platform Terms and Conditions

By using FixMate-SA, you agree to these terms:

1. SERVICE AGREEMENT
- FixMate-SA connects clients with independent service providers (fixers)
- All fixers are independent contractors, not employees of FixMate-SA
- Platform fee of R20 applies to each completed job

2. CLIENT OBLIGATIONS
- Accept terms before submitting service requests
- Provide accurate job descriptions and locations
- Allow fixer access to perform work as agreed
- Pay agreed amounts upon satisfactory completion

3. FIXER OBLIGATIONS
- Respond promptly to job notifications
- Complete accepted jobs or provide reasonable notice of cancellation
- Pay R20 platform fee for each completed job
- Maintain single job limit (one job at a time)

4. PAYMENT TERMS
- Platform fee of R20 per completed job
- Outstanding fees may restrict job assignment eligibility
- Admin may override restrictions in exceptional circumstances

5. QUALITY & MONITORING
- AI systems monitor fixer performance and behavior
- Persistent issues may result in account restrictions
- Fair job distribution algorithm ensures equitable opportunities

6. LIABILITY
- FixMate-SA facilitates connections but is not liable for work quality
- Disputes should be resolved directly between clients and fixers
- Emergency escalation available for urgent issues

7. TERMINATION
- Either party may terminate use at any time
- Outstanding fees remain payable after termination

By proceeding, you acknowledge understanding and acceptance of these terms.
                """.strip(),
                effective_date=datetime.utcnow(),
                is_current=True,
                acceptance_count=0
            )
            
            self.db.add(default_terms)
            self.db.commit()
            self.log("✅ Created default platform terms")
            return True
            
        except Exception as e:
            self.log(f"❌ Error creating default terms: {str(e)}", "ERROR")
            self.db.rollback()
            return False
    
    def initialize_fixer_availability(self):
        """Initialize availability records for existing fixers"""
        try:
            # Get all existing fixers without availability records
            fixers_without_availability = self.db.query(Fixer).outerjoin(FixerAvailability).filter(
                FixerAvailability.fixer_id == None
            ).all()
            
            count = 0
            for fixer in fixers_without_availability:
                availability = FixerAvailability(
                    fixer_id=fixer.id,
                    is_available=True,
                    has_outstanding_debt=False,  # Default to no debt
                    debt_amount=0.0,
                    is_suspended=False,
                    completion_rate=100.0,
                    reliability_score=100.0
                )
                self.db.add(availability)
                count += 1
            
            if count > 0:
                self.db.commit()
                self.log(f"✅ Initialized availability records for {count} fixers")
            else:
                self.log("ℹ️  All existing fixers already have availability records")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error initializing fixer availability: {str(e)}", "ERROR")
            self.db.rollback()
            return False
    
    def update_existing_jobs(self):
        """Update existing jobs with workflow defaults"""
        try:
            # Update jobs that don't have workflow fields set
            updated_count = 0
            
            # Get jobs that haven't been updated with workflow fields
            jobs_to_update = self.db.query(Job).filter(
                Job.terms_accepted.is_(None) | (Job.terms_accepted == False)
            ).all()
            
            for job in jobs_to_update:
                # Set terms as accepted for existing jobs (retroactive)
                job.terms_accepted = True
                job.terms_accepted_at = job.created_at
                
                # Set appropriate workflow stage based on current status
                if job.status == "completed":
                    job.workflow_stage = "completed"
                elif job.status == "cancelled":
                    job.workflow_stage = "cancelled"
                elif job.fixer_id:
                    job.workflow_stage = "assigned"
                else:
                    job.workflow_stage = "legacy"
                
                # Set default values for other workflow fields
                job.assignment_attempts = job.assignment_attempts or 0
                job.auto_reassignment_count = job.auto_reassignment_count or 0
                job.is_emergency_escalated = job.is_emergency_escalated or False
                job.priority_level = job.priority_level or "normal"
                job.tracking_active = job.tracking_active or False
                
                updated_count += 1
            
            if updated_count > 0:
                self.db.commit()
                self.log(f"✅ Updated {updated_count} existing jobs with workflow fields")
            else:
                self.log("ℹ️  All existing jobs already have workflow fields set")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error updating existing jobs: {str(e)}", "ERROR")
            self.db.rollback()
            return False
    
    def verify_migration(self):
        """Verify that the migration was successful"""
        self.log("🔍 Verifying migration...")
        
        # Check that all workflow tables exist
        workflow_tables = [
            'job_assignment_history', 'job_notifications', 'fixer_availability',
            'fixer_behavior_analysis', 'platform_terms', 'user_terms_acceptance'
        ]
        
        missing_tables = []
        for table in workflow_tables:
            if not self.table_exists(table):
                missing_tables.append(table)
        
        if missing_tables:
            self.log(f"❌ Missing tables: {', '.join(missing_tables)}", "ERROR")
            return False
        
        # Check that workflow columns exist in jobs table
        required_columns = [
            'terms_accepted', 'workflow_stage', 'assignment_timeout',
            'tracking_active', 'priority_level'
        ]
        
        missing_columns = []
        for column in required_columns:
            if not self.column_exists('jobs', column):
                missing_columns.append(column)
        
        if missing_columns:
            self.log(f"❌ Missing columns in jobs table: {', '.join(missing_columns)}", "ERROR")
            return False
        
        # Check that default terms exist
        terms_count = self.db.query(PlatformTerms).count()
        if terms_count == 0:
            self.log("❌ No platform terms found", "ERROR")
            return False
        
        self.log("✅ Migration verification successful!")
        return True
    
    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main migration function"""
    print("="*70)
    print("🚀 FixMate-SA Database Migration Tool")
    print("   Equivalent to 'flask db upgrade' for FastAPI")
    print("   Safe to run multiple times (idempotent)")
    print("="*70)
    
    migrator = None
    try:
        # Initialize migrator
        migrator = DatabaseMigrator()
        
        # Run migration
        success = migrator.migrate_workflow_system()
        
        if success:
            # Verify migration
            if migrator.verify_migration():
                print("\n" + "="*70)
                print("🎉 DATABASE MIGRATION COMPLETED SUCCESSFULLY!")
                print("✅ FixMate Job Workflow System is now active")
                print("✅ All features are ready for production use")
                print("="*70)
                return 0
            else:
                print("\n" + "="*70)
                print("⚠️  MIGRATION COMPLETED BUT VERIFICATION FAILED")
                print("❌ Please check the logs above for details")
                print("="*70)
                return 1
        else:
            print("\n" + "="*70)
            print("❌ DATABASE MIGRATION FAILED")
            print("❌ Please check the logs above for details")
            print("="*70)
            return 1
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        return 1
        
    finally:
        if migrator:
            migrator.close()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)