#!/usr/bin/env python3
"""
Force database recreation with all new fields
"""

import sys
import os
sys.path.append('/app/backend')

from database import drop_and_recreate_tables

def main():
    print("🔧 Force Database Recreation")
    print("=" * 50)
    
    try:
        print("📋 Dropping and recreating all database tables...")
        drop_and_recreate_tables()
        print("✅ Database tables recreated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database recreation failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)