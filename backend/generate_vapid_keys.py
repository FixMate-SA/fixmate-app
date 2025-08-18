#!/usr/bin/env python3
"""
Generate VAPID keys for push notifications
"""

from pywebpush import generate_vapid_keys_from_random
import json
import os

def generate_vapid_keys():
    """Generate VAPID public and private keys"""
    
    try:
        # Generate VAPID keys using pywebpush
        vapid_keys = generate_vapid_keys_from_random()
        
        public_key_b64 = vapid_keys['public_key']
        private_key_b64 = vapid_keys['private_key']
        
        print("🔑 VAPID Keys Generated Successfully!")
        print("=" * 50)
        print(f"Public Key (add to frontend): {public_key_b64}")
        print(f"Private Key (keep secure): {private_key_b64}")
        print("=" * 50)
        
        # Save to environment file
        env_path = "/app/backend/.env"
        
        # Read existing .env content
        env_content = ""
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_content = f.read()
        
        # Remove existing VAPID keys if present
        lines = env_content.split('\n')
        filtered_lines = []
        for line in lines:
            if not line.startswith(('VAPID_PUBLIC_KEY=', 'VAPID_PRIVATE_KEY=', 'VAPID_SUBJECT=')):
                filtered_lines.append(line)
        
        # Add new VAPID keys
        filtered_lines.extend([
            "",
            "# VAPID Keys for Push Notifications",
            f"VAPID_PUBLIC_KEY={public_key_b64}",
            f"VAPID_PRIVATE_KEY={private_key_b64}",
            "VAPID_SUBJECT=mailto:support@fixmate-sa.com"
        ])
        
        # Write back to .env
        with open(env_path, 'w') as f:
            f.write('\n'.join(filtered_lines))
        
        print("✅ VAPID keys saved to .env file")
        
        # Also save keys to a JSON file for backup
        vapid_keys_backup = {
            "public_key": public_key_b64,
            "private_key": private_key_b64,
            "subject": "mailto:support@fixmate-sa.com",
            "generated_at": "Generated using pywebpush"
        }
        
        with open("/app/backend/vapid_keys.json", 'w') as f:
            json.dump(vapid_keys_backup, f, indent=2)
        
        print("✅ VAPID keys backup saved to vapid_keys.json")
        print("\n🔒 IMPORTANT SECURITY NOTES:")
        print("1. Keep the private key secure and never share it publicly")
        print("2. The public key goes in your frontend application")
        print("3. Backup vapid_keys.json securely")
        print("4. If keys are compromised, regenerate new ones")
        
        return vapid_keys_backup
        
    except Exception as e:
        print(f"❌ Error generating VAPID keys: {e}")
        return None

if __name__ == "__main__":
    generate_vapid_keys()