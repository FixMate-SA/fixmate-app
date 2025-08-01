#!/usr/bin/env python3
"""
Database Migration Script for Enhanced Job Assignment Workflow
Adds new columns to existing tables to support the enhanced workflow system.
"""

import sys
import os
sys.path.append('/app/backend')

from database import engine
from sqlalchemy import text, Column, Integer, Float, Boolean, String, DateTime, Text
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_enhanced_workflow():
    """Apply database migrations for enhanced workflow system"""
    
    migrations = [
        # 1. Add new columns to FixerAvailability table
        {
            'table': 'fixer_availability',
            'columns': [
                'is_availability_frozen BOOLEAN DEFAULT FALSE',
                'availability_frozen_until TIMESTAMP',
                'freeze_reason VARCHAR',
                'minimum_rating_met BOOLEAN DEFAULT TRUE',
                'rating_penalty_applied FLOAT DEFAULT 0.0',
                'cancellation_penalty_count INTEGER DEFAULT 0',
                'platform_fee_status VARCHAR DEFAULT \'current\'',
                'platform_fee_overdue_since TIMESTAMP',
                'platform_fee_amount_due FLOAT DEFAULT 0.0'
            ]
        },
        
        # 2. Add new columns to Jobs table
        {
            'table': 'jobs',
            'columns': [
                'fixer_timeout_count INTEGER DEFAULT 0',
                'emergency_escalation_reason VARCHAR',
                'attendance_deadline TIMESTAMP',
                'fixer_freeze_applied BOOLEAN DEFAULT FALSE',
                'client_cancelled BOOLEAN DEFAULT FALSE',
                'client_cancellation_reason TEXT',
                'fixer_cancelled BOOLEAN DEFAULT FALSE',
                'fixer_cancellation_reason TEXT',
                'cancellation_penalties_applied TEXT',
                'platform_fee_due FLOAT DEFAULT 20.0',
                'platform_fee_status VARCHAR DEFAULT \'pending\'',
                'platform_fee_deadline TIMESTAMP',
                'platform_fee_paid_at TIMESTAMP',
                'fraud_risk_score FLOAT DEFAULT 0.0',
                'fraud_indicators TEXT',
                'ai_monitoring_active BOOLEAN DEFAULT TRUE',
                'admin_attention_flagged BOOLEAN DEFAULT FALSE'
            ]
        },
        
        # 3. Add new columns to Fixers table
        {
            'table': 'fixers',
            'columns': [
                'base_rating FLOAT DEFAULT 0.0',
                'rating_penalty_total FLOAT DEFAULT 0.0',
                'minimum_rating_threshold FLOAT DEFAULT 3.0',
                'is_new_fixer BOOLEAN DEFAULT TRUE',
                'jobs_completed INTEGER DEFAULT 0',
                'jobs_cancelled INTEGER DEFAULT 0',
                'jobs_incomplete INTEGER DEFAULT 0',
                'jobs_no_show INTEGER DEFAULT 0',
                'completion_percentage FLOAT DEFAULT 100.0',
                'cancellation_penalty_count INTEGER DEFAULT 0',
                'last_cancellation_penalty TIMESTAMP',
                'availability_freeze_count INTEGER DEFAULT 0',
                'total_freeze_hours INTEGER DEFAULT 0',
                'platform_fees_owed FLOAT DEFAULT 0.0',
                'platform_fees_paid FLOAT DEFAULT 0.0',
                'fee_payment_overdue BOOLEAN DEFAULT FALSE',
                'fee_suspension_applied BOOLEAN DEFAULT FALSE'
            ]
        }
    ]
    
    try:
        with engine.begin() as conn:
            logger.info("Starting Enhanced Job Assignment Workflow database migration...")
            
            for migration in migrations:
                table_name = migration['table']
                logger.info(f"Migrating table: {table_name}")
                
                for column_def in migration['columns']:
                    column_name = column_def.split()[0]
                    
                    # Check if column already exists
                    check_query = text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = :table_name AND column_name = :column_name
                    """)
                    
                    result = conn.execute(check_query, {
                        'table_name': table_name,
                        'column_name': column_name
                    })
                    
                    if result.fetchone():
                        logger.info(f"  Column {column_name} already exists, skipping...")
                        continue
                    
                    # Add the column
                    alter_query = text(f"ALTER TABLE {table_name} ADD COLUMN {column_def}")
                    conn.execute(alter_query)
                    logger.info(f"  ✅ Added column: {column_name}")
            
            logger.info("✅ Enhanced Job Assignment Workflow migration completed successfully!")
            
            # Update base_rating for existing fixers
            logger.info("Updating base_rating for existing fixers...")
            update_base_rating = text("""
                UPDATE fixers 
                SET base_rating = rating 
                WHERE base_rating = 0.0 AND rating > 0.0
            """)
            result = conn.execute(update_base_rating)
            logger.info(f"  ✅ Updated base_rating for {result.rowcount} fixers")
            
            # Mark existing fixers as not new if they have jobs
            logger.info("Updating is_new_fixer status...")
            update_new_fixer = text("""
                UPDATE fixers 
                SET is_new_fixer = FALSE 
                WHERE total_jobs > 0
            """)
            result = conn.execute(update_new_fixer)
            logger.info(f"  ✅ Updated is_new_fixer for {result.rowcount} fixers")
            
            # Copy job counts to new columns
            logger.info("Updating job statistics...")
            update_job_stats = text("""
                UPDATE fixers 
                SET jobs_completed = total_jobs 
                WHERE jobs_completed = 0 AND total_jobs > 0
            """)
            result = conn.execute(update_job_stats)
            logger.info(f"  ✅ Updated job statistics for {result.rowcount} fixers")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise
    
    logger.info("🎉 Enhanced Job Assignment Workflow database migration completed!")

if __name__ == "__main__":
    migrate_enhanced_workflow()