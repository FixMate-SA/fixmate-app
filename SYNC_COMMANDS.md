# Quick Sync Commands for Emergent → Production Deployment

## 🚀 URGENT: Files That Must Be Copied to Your Local Repository

### Core Backend Files (Copy these exactly):

**1. Backend Models** - Copy content of `/app/backend/models.py`
- Contains: `Announcement` and `AnnouncementChat` models (lines 958-1007)
- Critical: Includes `__table_args__ = {'extend_existing': True}` fix

**2. Backend API Server** - Copy content of `/app/backend/server.py` 
- Contains: 8 new announcement API endpoints
- Search for functions containing "announcement" to find the new code

**3. Database Migration Script** - Copy `/app/backend/create_announcement_tables.py`
- This is a NEW file that creates the database tables
- Must be run on Heroku after deployment

### Core Frontend Files (Copy these exactly):

**4. Admin Management Component** - Copy `/app/frontend/src/components/Admin/AnnouncementManagement.js`
- This is a NEW file with full admin interface

**5. User Display Component** - Copy `/app/frontend/src/components/Common/AnnouncementDisplay.js` 
- This is a NEW file that shows announcements to users

**6. API Service Methods** - Copy updated `/app/frontend/src/services/api.js`
- Contains new announcement API methods (lines 250-292)

**7. Dashboard Integrations:**
- Copy updated `/app/frontend/src/components/Admin/AdminDashboard.js` (added Announcements tab)
- Copy updated `/app/frontend/src/components/Dashboard/Dashboard.js` (added AnnouncementDisplay)

## ⚙️ CONFIGURATION CHANGES

### Environment Variables (CRITICAL):

**Update `/frontend/.env` in your local repo:**
```
REACT_APP_BACKEND_URL=https://your-heroku-app-name.herokuapp.com
```

**Verify `/backend/.env` has:**
```
DATABASE_URL=your-heroku-postgres-connection-string
```

## 🗄️ DATABASE SETUP ON HEROKU

After deploying code changes, run this command on Heroku:

```bash
heroku run python create_announcement_tables.py --app your-heroku-app-name
```

## 🔍 VERIFICATION COMMANDS

Test these URLs after deployment:

```bash
# Check if backend is responding:
curl https://your-heroku-app.herokuapp.com/api/announcements

# Check if tables exist:
heroku pg:psql --app your-app-name
\dt announcements*
```

## 🎯 EXACT FILES TO FOCUS ON

**If you can only copy a few files, prioritize these 7:**

1. `/backend/models.py` (database models)
2. `/backend/server.py` (API endpoints) 
3. `/backend/create_announcement_tables.py` (migration script)
4. `/frontend/src/components/Admin/AnnouncementManagement.js` (admin UI)
5. `/frontend/src/components/Common/AnnouncementDisplay.js` (user UI)
6. `/frontend/src/services/api.js` (API calls)
7. `/frontend/.env` (configuration)

## 🚨 CRITICAL SUCCESS CHECKLIST

After deployment, verify:

- [ ] Can log in as admin
- [ ] Admin dashboard shows announcement section
- [ ] Can create new announcements  
- [ ] Can log in as client/fixer
- [ ] Users see announcements on dashboard
- [ ] Chat functionality works
- [ ] No console errors in browser

---

**Next Steps After File Sync:**
1. Copy files to local repository
2. Update .env files with production URLs
3. Commit and push to GitHub
4. Run database migration on Heroku
5. Test the live application

**Need Help?** The announcement system is fully functional in Emergent. All code exists and works perfectly - it just needs to be copied to your production environment.