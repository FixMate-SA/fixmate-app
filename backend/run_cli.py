#!/usr/bin/env python3
"""
Helper script to run FixMate-SA CLI commands
Usage: python run_cli.py <command> [args...]
"""

import sys
import subprocess
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_cli.py <command> [args...]")
        print("\nAvailable commands:")
        print("  add-fixer <name> <phone> <skills>")
        print("  promote-admin <phone>")
        print("  demote-admin <phone>")
        print("  remove-fixer <phone>")
        print("  remove-client <phone>")
        print("  analyze-data")
        print("  stats")
        print("  list-admins")
        print("  toggle-fixer-active <phone>")
        print("  list-jobs [--status <status>] [--limit <limit>]")
        print("  reassign-job <job_id> <fixer_phone>")
        print("  remove-all-clients")
        print("  send-whatsapp <phone> <message>")
        print("  generate-insight")
        print("  list-insights [--limit <limit>]")
        print("  backup-data <output_file>")
        return
    
    # Get the backend directory
    backend_dir = Path(__file__).parent
    cli_script = backend_dir / "fixmate-cli"
    
    # Build command
    cmd = [sys.executable, str(cli_script)] + sys.argv[1:]
    
    try:
        # Run the command
        result = subprocess.run(cmd, cwd=backend_dir, capture_output=False)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running command: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()