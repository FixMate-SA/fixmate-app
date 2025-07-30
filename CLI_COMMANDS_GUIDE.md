# FixMate-SA CLI Commands Guide

## 🚀 **Working Commands - Ready to Use**

The exact command you wanted is now working perfectly! Here are all available options:

### ✅ **Add Fixer Commands (EXACTLY what you requested)**

```bash
# Add fixer WITHOUT password
python run_cli.py add-fixer "John Smith" "0821111111" "plumbing,electrical,geysers"

# Add fixer WITH password
python run_cli.py add-fixer-pwd "John Smith" "0821111111" "plumbing,electrical,geysers" "fixer123"

# Add fixer with optional password
python run_cli.py add-fixer "John Smith" "0821111111" "plumbing,electrical,geysers" "fixer123"
```

### 🔧 **What the Command Does:**
- ✅ Creates a new User account with proper name fields
- ✅ Creates a Fixer profile with skills and services
- ✅ Sets password if provided (enables web/app login)
- ✅ Auto-approves the fixer (ready to work immediately)
- ✅ Creates FixerAvailability record (for workflow system)
- ✅ Parses skills properly (comma-separated)
- ✅ Formats phone number correctly (+27...)

### 📋 **Other Useful Commands**

```bash
# Database management
python run_cli.py migrate              # Run database migrations
python run_cli.py check-db             # Check database status

# User management
python run_cli.py set-password "0821111111" "newpassword"
python run_cli.py promote-admin "0821111111"
python run_cli.py list-fixers
python run_cli.py stats

# Help
python run_cli.py help
```

## 🌐 **Heroku Usage**

```bash
# On Heroku (production)
heroku run python backend/run_cli.py add-fixer-pwd "John Smith" "0821111111" "plumbing,electrical,geysers" "fixer123"

# Run migration on Heroku
heroku run python backend/run_cli.py migrate

# Check fixers on Heroku
heroku run python backend/run_cli.py list-fixers
```

## 📊 **Command Output Example**

```
🚀 Running: manage.py add-fixer-pwd John Smith 0821111111 plumbing,electrical,geysers fixer123
----------------------------------------
✅ Created new user: John Smith
✅ Password set for user: fixer123
✅ Successfully added fixer: 'John Smith' with phone +27821111111
   Skills: plumbing,electrical,geysers
   Services JSON: ["plumbing", "electrical", "geysers"]
   Status: Approved and available for jobs
   Login: +27821111111 / ***SET***
----------------------------------------
✅ Command completed successfully!
```

## 🔐 **Login Credentials Created**

When you use the password commands, fixers can login with:
- **Phone**: The phone number you provided (formatted as +27...)
- **Password**: The password you set
- **Access**: Full fixer dashboard, job board, workflow features

## ✨ **Features Activated**

Each fixer created gets:
- ✅ **User Account** - Can login to web app
- ✅ **Fixer Profile** - Shows in fixer lists  
- ✅ **Job Eligibility** - Can receive and accept jobs
- ✅ **Workflow Integration** - Full workflow system access
- ✅ **Skills Matching** - Gets jobs matching their skills
- ✅ **WhatsApp Integration** - Can receive WhatsApp notifications
- ✅ **Payment System** - Ready for R20 per job fee processing

## 🚨 **Important Notes**

1. **Phone Format**: Numbers are automatically formatted to +27... format
2. **Skills Format**: Use comma-separated values (no spaces after commas)
3. **Password**: If no password set, user can't login via web/app (WhatsApp only)
4. **Auto-Approval**: CLI-created fixers are auto-approved and ready to work
5. **Duplicate Check**: Command prevents creating duplicate fixers

## 🎯 **Perfect for Your Needs**

This command system is ideal for:
- **Bulk Adding Fixers**: Quick setup for multiple fixers
- **Testing**: Create test fixers with known credentials  
- **Production Setup**: Add real fixers with secure passwords
- **Heroku Deployment**: Works perfectly on production

Your original command now works exactly as you wanted! 🎉