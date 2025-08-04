#!/usr/bin/env python3
"""
Create default platform terms for FixMate-SA
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import get_db
from models import PlatformTerms
import uuid
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_default_terms():
    """Create default platform terms if none exist"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if terms already exist
        existing_terms = db.query(PlatformTerms).filter(PlatformTerms.is_current == True).first()
        
        if existing_terms:
            logger.info("✅ Current platform terms already exist")
            return True
        
        # Create default terms
        default_terms = PlatformTerms(
            id=str(uuid.uuid4()),
            version="1.0",
            title="FixMate-SA Terms of Service",
            content="""
# FixMate-SA Terms of Service

## 1. Service Overview
FixMate-SA connects clients with verified service providers (fixers) for various home and business services.

## 2. Platform Fee
- A platform fee of R20 applies to each completed job
- Fixers earn this fee upon successful job completion
- Payment is processed automatically upon job completion

## 3. User Responsibilities

### Clients:
- Provide accurate job descriptions
- Be present during service delivery
- Rate fixers after job completion
- Pay agreed-upon service fees

### Fixers:
- Provide quality service as described
- Arrive on time for appointments
- Complete work to client satisfaction
- Upload before/after photos for verification

## 4. Job Workflow
- Clients create service requests
- System notifies eligible fixers
- First available fixer accepts the job
- Fixer completes work with photo documentation
- Client rates and reviews the service
- R20 platform fee is credited to fixer

## 5. Quality Assurance
- Photo verification required for job completion
- Rating system maintains service quality
- Dispute resolution available if needed

## 6. Payment Terms
- Fixers receive R20 per completed job
- Clients pay service fees directly to fixers
- Platform fees are automatically processed

## 7. Data Protection
Your personal information is protected in accordance with South African data protection laws.

## 8. Modifications
These terms may be updated periodically. Users will be notified of changes.

Last updated: """ + datetime.utcnow().strftime("%Y-%m-%d"),
            is_current=True,
            created_at=datetime.utcnow(),
            effective_date=datetime.utcnow()
        )
        
        db.add(default_terms)
        db.commit()
        
        logger.info("✅ Default platform terms created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating default terms: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    success = create_default_terms()
    if success:
        print("✅ Default terms creation completed!")
    else:
        print("❌ Default terms creation failed!")
        sys.exit(1)