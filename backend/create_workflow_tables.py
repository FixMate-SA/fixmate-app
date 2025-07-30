"""
Script to create the new workflow tables for the FixMate Job Workflow System
Run this script to add the new tables to the existing database.
"""

from sqlalchemy import create_engine, text
from database import engine
from models import (
    Base, JobAssignmentHistory, JobNotification, FixerAvailability, 
    FixerBehaviorAnalysis, PlatformTerms, UserTermsAcceptance
)
import os
from datetime import datetime

def create_workflow_tables():
    """Create the new workflow tables"""
    try:
        print("Creating workflow tables...")
        
        # Create the new tables
        Base.metadata.create_all(bind=engine)
        print("✅ All workflow tables created successfully")
        
        # Insert default platform terms
        create_default_platform_terms()
        
        # Initialize fixer availability records for existing fixers
        initialize_fixer_availability()
        
        print("🎉 Workflow system setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error creating workflow tables: {str(e)}")
        return False
    
    return True

def create_default_platform_terms():
    """Create default platform terms"""
    try:
        from sqlalchemy.orm import sessionmaker
        from models import PlatformTerms
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if terms already exist
        existing_terms = db.query(PlatformTerms).first()
        if existing_terms:
            print("ℹ️ Platform terms already exist")
            db.close()
            return
        
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
            is_current=True
        )
        
        db.add(default_terms)
        db.commit()
        db.close()
        
        print("✅ Default platform terms created")
        
    except Exception as e:
        print(f"❌ Error creating default terms: {str(e)}")

def initialize_fixer_availability():
    """Initialize availability records for existing fixers"""
    try:
        from sqlalchemy.orm import sessionmaker
        from models import Fixer, FixerAvailability
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Get all existing fixers
        fixers = db.query(Fixer).all()
        
        for fixer in fixers:
            # Check if availability record exists
            existing_availability = db.query(FixerAvailability).filter(
                FixerAvailability.fixer_id == fixer.id
            ).first()
            
            if not existing_availability:
                availability = FixerAvailability(
                    fixer_id=fixer.id,
                    is_available=True,
                    has_outstanding_debt=(fixer.payment_status != "current"),
                    debt_amount=0.0 if fixer.payment_status == "current" else 20.0
                )
                db.add(availability)
        
        db.commit()
        db.close()
        
        print(f"✅ Initialized availability records for {len(fixers)} fixers")
        
    except Exception as e:
        print(f"❌ Error initializing fixer availability: {str(e)}")

def update_existing_jobs():
    """Update existing jobs with workflow fields"""
    try:
        from sqlalchemy.orm import sessionmaker
        from models import Job
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Update existing jobs to have terms accepted (retroactively)
        existing_jobs = db.query(Job).filter(Job.terms_accepted == False).all()
        
        for job in existing_jobs:
            job.terms_accepted = True
            job.terms_accepted_at = job.created_at
            job.workflow_stage = "completed" if job.status == "completed" else "legacy"
        
        db.commit()
        db.close()
        
        print(f"✅ Updated {len(existing_jobs)} existing jobs with workflow fields")
        
    except Exception as e:
        print(f"❌ Error updating existing jobs: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting FixMate Workflow System Setup...")
    
    success = create_workflow_tables()
    
    if success:
        update_existing_jobs()
        print("\n🎉 FixMate Job Workflow System is now ready!")
        print("\nNew features available:")
        print("- ✅ Mandatory terms acceptance")
        print("- ✅ Enhanced fixer eligibility checking") 
        print("- ✅ Simultaneous fixer notifications")
        print("- ✅ First come, first serve assignment")
        print("- ✅ Live tracking system")
        print("- ✅ Timeout and reallocation")
        print("- ✅ R20 per job completion fee")
        print("- ✅ AI behavior monitoring")
        print("- ✅ Admin override capabilities")
        print("- ✅ Single job limit enforcement")
    else:
        print("\n❌ Setup failed. Please check the errors above.")