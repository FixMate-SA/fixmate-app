#!/usr/bin/env python3
"""
FixMate-SA Root CLI Wrapper
This script forwards commands to the backend CLI runner
Works with Heroku's /app root directory structure
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Forward all commands to the backend CLI runner"""
    try:
        # Get the app root directory (where this script is located)
        app_root = Path(__file__).parent
        
        # Path to the actual backend CLI script
        backend_cli = app_root / "backend" / "run_cli.py"
        
        # Verify the backend script exists
        if not backend_cli.exists():
            print(f"❌ Backend CLI script not found at: {backend_cli}")
            print("   Expected location: /app/backend/run_cli.py")
            return 1
        
        # Build the command to run the backend CLI
        cmd = [sys.executable, str(backend_cli)] + sys.argv[1:]
        
        # Show what we're running (for debugging)
        print(f"🔧 Forwarding to backend CLI: {' '.join(cmd[2:])}")
        print("-" * 50)
        
        # Run the backend CLI script
        result = subprocess.run(
            cmd, 
            cwd=app_root,  # Set working directory to app root
            capture_output=False
        )
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running CLI command: {e}")
        print(f"   Working directory: {os.getcwd()}")
        print(f"   Script location: {__file__}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)