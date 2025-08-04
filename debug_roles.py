#!/usr/bin/env python3
"""
Debug Roles Script - Check database and role service directly
"""

import sys
import os
sys.path.append('/app/backend')

from database import get_db
from models import User, Fixer
from services.role_service import role_service

def debug_roles():
    print("🔍 DEBUGGING ROLES AND DATABASE")
    print("=" * 80)
    
    db = next(get_db())
    
    # Check admin user
    print("🔑 ADMIN USER DEBUG:")
    admin_phones = ["+27800000001", "whatsapp:+27800000001"]
    for phone in admin_phones:
        user = db.query(User).filter(User.phone == phone).first()
        if user:
            print(f"   Found user with phone: {phone}")
            print(f"   User ID: {user.id}")
            print(f"   Database role: {user.role}")
            
            # Check role service determination
            role_info = role_service.determine_user_role(phone, db)
            print(f"   Role service role: {role_info['role']}")
            
            # Check if phone is in admin list
            print(f"   Phone in admin list: {phone in role_service.admin_phones}")
            print(f"   Admin phones: {role_service.admin_phones}")
            break
    else:
        print("   ❌ Admin user not found in database")
    
    print()
    
    # Check client user
    print("👤 CLIENT USER DEBUG:")
    client_phones = ["+27800000002", "whatsapp:+27800000002"]
    for phone in client_phones:
        user = db.query(User).filter(User.phone == phone).first()
        if user:
            print(f"   Found user with phone: {phone}")
            print(f"   User ID: {user.id}")
            print(f"   Database role: {user.role}")
            
            # Check role service determination
            role_info = role_service.determine_user_role(phone, db)
            print(f"   Role service role: {role_info['role']}")
            break
    else:
        print("   ❌ Client user not found in database")
    
    print()
    
    # Check fixer user
    print("🔧 FIXER USER DEBUG:")
    fixer_phones = ["+27800000003", "whatsapp:+27800000003"]
    for phone in fixer_phones:
        user = db.query(User).filter(User.phone == phone).first()
        if user:
            print(f"   Found user with phone: {phone}")
            print(f"   User ID: {user.id}")
            print(f"   Database role: {user.role}")
            
            # Check role service determination
            role_info = role_service.determine_user_role(phone, db)
            print(f"   Role service role: {role_info['role']}")
            
            # Check fixer record
            fixer = db.query(Fixer).filter(Fixer.phone == phone).first()
            if fixer:
                print(f"   Fixer record found: {fixer.id}")
                print(f"   Fixer services: {fixer.services}")
            else:
                print("   ❌ No fixer record found")
            break
    else:
        print("   ❌ Fixer user not found in database")
    
    db.close()

if __name__ == "__main__":
    debug_roles()