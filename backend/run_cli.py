#!/usr/bin/env python3
"""
FixMate-SA CLI Runner - Enhanced version with password support
Usage: python run_cli.py <command> [args...]
This provides the exact command format requested with password support
"""

import sys
import subprocess
from pathlib import Path

def show_help():
    """Show enhanced CLI commands"""
    print("FixMate-SA CLI Runner - Enhanced Version")
    print("=" * 45)
    print("Fixer Management (NEW - with password support):")
    print("  add-fixer \"Name\" \"phone\" \"skill1,skill2,skill3\" [password]")
    print("  add-fixer-pwd \"Name\" \"phone\" \"skill1,skill2,skill3\" \"password\"")
    print()
    print("Database Management:")
    print("  migrate                    - Run database migration")
    print("  check-db                   - Check database status")
    print()
    print("User Management:")
    print("  set-password \"phone\" \"password\"")
    print("  promote-admin \"phone\"")
    print("  list-users")
    print("  list-fixers")
    print("  stats")
    print()
    print("Examples (EXACTLY what you requested):")
    print("  python run_cli.py add-fixer \"John Smith\" \"0821111111\" \"plumbing,electrical,geysers\"")
    print("  python run_cli.py add-fixer-pwd \"John Smith\" \"0821111111\" \"plumbing,electrical,geysers\" \"fixer123\"")
    print("  python run_cli.py set-password \"0821111111\" \"fixer123\"")
    print()
    print("Heroku Usage:")
    print("  heroku run python backend/run_cli.py add-fixer-pwd \"John Smith\" \"0821111111\" \"plumbing,electrical,geysers\" \"fixer123\"")
    print("=" * 45)

def main():
    if len(sys.argv) < 2:
        show_help()
        return 1
    
    command = sys.argv[1].lower()
    
    if command in ['help', '-h', '--help']:
        show_help()
        return 0
    
    # Get the backend directory
    backend_dir = Path(__file__).parent
    manage_script = backend_dir / "manage.py"
    
    # Build command to run manage.py with same arguments
    cmd = [sys.executable, str(manage_script)] + sys.argv[1:]
    
    try:
        print(f"🚀 Running: {' '.join(cmd[1:])}")
        print("-" * 40)
        
        # Run the command
        result = subprocess.run(cmd, cwd=backend_dir, capture_output=False)
        
        print("-" * 40)
        if result.returncode == 0:
            print("✅ Command completed successfully!")
        else:
            print(f"❌ Command failed with exit code {result.returncode}")
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return 1

if __name__ == "__main__":
    main()