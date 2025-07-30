# FixMate-SA Heroku Migration Guide

This guide explains how to run database migrations on Heroku after deploying the new FixMate Job Workflow System.

## 🚀 Quick Migration Commands

### 1. Check Database Status (Optional)
```bash
heroku run python backend/manage.py check-db
```

### 2. Run Migration (Main Command)
```bash
heroku run python backend/manage.py migrate
```

### 3. Verify Migration Success
```bash
heroku run python backend/manage.py stats
```

## 📋 Complete Migration Process

### Step 1: Deploy Your Code to Heroku
```bash
git add .
git commit -m "Add FixMate Job Workflow System"
git push heroku main
```

### Step 2: Check Database Connection
```bash
heroku run python backend/manage.py check-db
```
**Expected Output:**
```
🔍 Checking database connection...
✅ Database connection successful
⚠️  Missing tables: platform_terms, fixer_availability, job_assignment_history
💡 Run 'python backend/manage.py migrate' to create missing tables
```

### Step 3: Run Database Migration
```bash
heroku run python backend/manage.py migrate
```
**Expected Output:**
```
======================================================================
🚀 FixMate-SA Database Migration Tool
   Equivalent to 'flask db upgrade' for FastAPI
   Safe to run multiple times (idempotent)
======================================================================
[TIMESTAMP] INFO: 🚀 Starting FixMate Workflow System Migration
[TIMESTAMP] INFO: 📋 Creating new workflow tables...
[TIMESTAMP] INFO: ✅ Created table 'job_assignment_history'
[TIMESTAMP] INFO: ✅ Created table 'job_notifications'
[TIMESTAMP] INFO: ✅ Created table 'fixer_availability'
[TIMESTAMP] INFO: ✅ Created table 'fixer_behavior_analysis'
[TIMESTAMP] INFO: ✅ Created table 'platform_terms'
[TIMESTAMP] INFO: ✅ Created table 'user_terms_acceptance'
[TIMESTAMP] INFO: 🔧 Adding workflow columns to jobs table...
[TIMESTAMP] INFO: ✅ Added column 'terms_accepted' to table 'jobs'
[TIMESTAMP] INFO: ✅ Added column 'workflow_stage' to table 'jobs'
[TIMESTAMP] INFO: ✅ Created default platform terms
[TIMESTAMP] INFO: ✅ Initialized availability records for X fixers
[TIMESTAMP] INFO: ✅ Updated X existing jobs with workflow fields
[TIMESTAMP] INFO: 🎉 Migration completed: 26/26 steps successful
[TIMESTAMP] INFO: ✅ All workflow system features are now active!

======================================================================
🎉 DATABASE MIGRATION COMPLETED SUCCESSFULLY!
✅ FixMate Job Workflow System is now active
✅ All features are ready for production use
======================================================================
```

### Step 4: Verify Migration Success
```bash
heroku run python backend/manage.py check-db
```
**Expected Output:**
```
🔍 Checking database connection...
✅ Database connection successful
✅ Found 6 core tables
```

## 🔧 Workflow System Features Now Active

After successful migration, the following features are available:

### 1. **Mandatory Terms Acceptance** ✅
- Users must accept platform terms before job creation
- Terms are version-controlled with acceptance tracking

### 2. **Enhanced Job Creation** ✅
- Complete workflow with eligibility checking
- Location-based fixer matching
- Debt and availability validation

### 3. **First Come, First Serve Assignment** ✅
- Race-condition-free job assignment
- Simultaneous notifications to all eligible fixers
- WhatsApp + In-app notifications

### 4. **Live Tracking System** ✅
- Real-time fixer location updates
- Estimated arrival calculations
- Client notification system

### 5. **Timeout & Emergency Escalation** ✅
- Automatic job reassignment on timeout
- Emergency priority for critical jobs
- Multiple attempt handling

### 6. **R20 Per Job Fee System** ✅
- Automatic platform fee processing
- Payment status tracking
- Debt management integration

### 7. **AI Behavior Analysis** ✅
- Pattern detection for fixer performance
- Reliability scoring
- Admin alerts for problematic behavior

### 8. **Admin Override Capabilities** ✅
- Manual restriction management
- Emergency job reassignment
- System monitoring tools

### 9. **Single Job Limit Enforcement** ✅
- Prevents fixers from accepting multiple jobs
- Availability status management
- Automatic availability updates

## 🛠️ Additional Management Commands

### Create Admin User
```bash
heroku run python backend/manage.py promote-admin +27821234567
heroku run python backend/manage.py set-password +27821234567 admin123
```

### Add Test Fixers
```bash
heroku run python backend/manage.py add-fixer "John Plumber" +27821111111 "plumbing, general repairs"
heroku run python backend/manage.py add-fixer "Sarah Electrician" +27822222222 "electrical, lighting"
```

### Check System Status
```bash
heroku run python backend/manage.py stats
```

### View All Users
```bash
heroku run python backend/manage.py list-users
heroku run python backend/manage.py list-fixers
```

## 🚨 Troubleshooting

### Migration Fails with "Table already exists"
This is normal! The migration script is idempotent (safe to run multiple times). Just run:
```bash
heroku run python backend/manage.py migrate
```

### Database Connection Error
Check your Heroku PostgreSQL add-on:
```bash
heroku pg:info
heroku config | grep DATABASE_URL
```

### Missing Tables After Migration
Run the migration again - it's safe:
```bash
heroku run python backend/manage.py migrate
```

### Check Heroku Logs
```bash
heroku logs --tail
```

## 📊 Migration Script Features

- **Idempotent**: Safe to run multiple times
- **Rollback Safe**: Doesn't delete existing data  
- **Progress Tracking**: Shows detailed progress logs
- **Verification**: Automatically verifies migration success
- **Error Handling**: Graceful failure handling with detailed error messages

## 🎯 API Endpoints Now Available

After migration, these new workflow API endpoints are active:

### Terms Management
- `GET /api/terms/check/{user_id}` - Check terms acceptance
- `POST /api/terms/accept` - Accept platform terms

### Enhanced Job Management  
- `POST /api/jobs/workflow` - Create job with workflow validation
- `GET /api/jobs/{job_id}/workflow-status` - Get real-time job status
- `POST /api/jobs/{job_id}/accept` - Fixer accept job
- `POST /api/jobs/{job_id}/complete` - Complete job with fee processing

### Live Tracking
- `POST /api/fixer/{fixer_id}/location` - Update fixer location
- `GET /api/fixer/{fixer_id}/eligible-jobs` - Get available jobs

### AI & Admin
- `GET /api/fixer/{fixer_id}/behavior-analysis` - Get AI analysis
- `POST /api/admin/fixer/{fixer_id}/override` - Admin override restrictions

## ✅ Success Indicators

Your migration is successful when:

1. **Migration command exits with code 0**
2. **All 26 migration steps show ✅**
3. **check-db command shows "Found 6 core tables"**
4. **Your app loads without database errors**
5. **New workflow features are accessible in the UI**

## 📞 Support

If you encounter any issues during migration:

1. Check Heroku logs: `heroku logs --tail`
2. Run database check: `heroku run python backend/manage.py check-db`  
3. Try migration again: `heroku run python backend/manage.py migrate`
4. Verify with stats: `heroku run python backend/manage.py stats`

The migration system is designed to be robust and handle edge cases gracefully. It's safe to run multiple times and will not corrupt existing data.

---

**🎉 After successful migration, your FixMate-SA platform will have all the comprehensive workflow system features active and ready for production use!**