import json
import requests
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# 360dialog API configuration
API_URL = "https://waba-v2.360dialog.io/v1/messages"
API_KEY = os.environ.get('D360_API_KEY')  # Set this in your Heroku config vars

def send_whatsapp_message(to_number, message_body):
    """Send WhatsApp message using 360dialog API"""
    
    # Clean the phone number (remove whatsapp: prefix if present)
    clean_number = to_number.replace('whatsapp:', '')
    
    # Create the payload - this is the corrected format
    payload = {
        "to": clean_number,
        "type": "text",
        "text": {
            "body": message_body
        }
    }
    
    headers = {
        'D360-API-KEY': API_KEY,
        'Content-Type': 'application/json'
    }
    
    print(f"🟡 Sending to: {clean_number}")
    print(f"📦 Message: {message_body}")
    print(f"🔁 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        print(f"✅ HTTP Status: {response.status_code}")
        print(f"🔽 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Message sent successfully!")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception sending message: {str(e)}")
        return False

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages"""
    try:
        # Get the webhook data
        webhook_data = request.get_json()
        print(f"Received 360dialog webhook: {json.dumps(webhook_data, indent=2)}")
        
        # Extract message details
        if 'entry' in webhook_data:
            for entry in webhook_data['entry']:
                if 'changes' in entry:
                    for change in entry['changes']:
                        if 'value' in change and 'messages' in change['value']:
                            for message in change['value']['messages']:
                                # Get sender and message content
                                sender = message['from']
                                message_type = message['type']
                                
                                if message_type == 'text':
                                    user_message = message['text']['body']
                                    print(f"📱 Message from {sender}: {user_message}")
                                    
                                    # Handle different message types
                                    response_message = handle_user_message(user_message, sender)
                                    
                                    # Send response
                                    if response_message:
                                        send_whatsapp_message(sender, response_message)
                                
                                elif message_type == 'location':
                                    # Handle location sharing
                                    latitude = message['location']['latitude']
                                    longitude = message['location']['longitude']
                                    print(f"📍 Location from {sender}: {latitude}, {longitude}")
                                    
                                    response_message = handle_location(latitude, longitude, sender)
                                    if response_message:
                                        send_whatsapp_message(sender, response_message)
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def handle_user_message(message, sender):
    """Process user messages and return appropriate response"""
    message_lower = message.lower().strip()
    
    # Greeting responses
    if message_lower in ['hi', 'hello', 'hey', 'start']:
        return """👋 Hi there! Welcome to FixMate South Africa!

I'm here to help you find reliable fixers for your home and business needs.

What service do you need help with today? 
(e.g., plumbing, electrical, painting, carpentry, etc.)"""
    
    # Service request
    elif any(service in message_lower for service in ['plumb', 'electric', 'paint', 'carpen', 'fix', 'repair']):
        # Set user state to awaiting location
        set_user_state(sender, 'awaiting_location', {'service': message})
        return """Got it! To help us find the nearest fixer, please share your location.

📍 Tap the paperclip icon 📎, then choose 'Location'."""
    
    # Help or unknown message
    else:
        return """I can help you find fixers for various services like:
• Plumbing 🔧
• Electrical work ⚡
• Painting 🎨
• Carpentry 🔨
• General repairs 🛠️

Just tell me what service you need!"""

def handle_location(latitude, longitude, sender):
    """Handle location sharing and find nearby fixers"""
    try:
        # Get user state
        user_state = get_user_state(sender)
        
        if user_state and user_state.get('state') == 'awaiting_location':
            service = user_state.get('data', {}).get('service', 'general repair')
            
            # Here you would typically:
            # 1. Query your database for nearby fixers
            # 2. Filter by service type
            # 3. Return top matches
            
            # For now, return a placeholder response
            return f"""🎯 Perfect! I found your location.

Looking for {service} specialists near you...

📋 Here are 3 top-rated fixers in your area:

1. **Mike's Plumbing** ⭐⭐⭐⭐⭐
   📞 078 123 4567
   📍 2.3km away
   
2. **Quick Fix Solutions** ⭐⭐⭐⭐
   📞 082 987 6543  
   📍 3.1km away
   
3. **Reliable Repairs** ⭐⭐⭐⭐⭐
   📞 071 555 7890
   📍 4.2km away

💬 Reply with a number (1-3) to get contact details, or type 'more' for additional options."""
        
        else:
            return "Thanks for sharing your location! Please tell me what service you need first."
            
    except Exception as e:
        print(f"❌ Error handling location: {str(e)}")
        return "Thanks for your location! Let me find fixers for you..."

# Simple state management (in production, use Redis or database)
user_states = {}

def set_user_state(user_id, state, data=None):
    """Set user conversation state"""
    user_states[user_id] = {
        'state': state,
        'data': data or {}
    }
    print(f"State for {user_id} set to {state} with data: {data}")

def get_user_state(user_id):
    """Get user conversation state"""
    return user_states.get(user_id)

@app.route('/')
def home():
    """Health check endpoint"""
    return """
    <h1>FixMate WhatsApp Bot</h1>
    <p>✅ Bot is running</p>
    <p>📱 Ready to receive WhatsApp messages</p>
    <p>🔧 Connecting you with trusted fixers</p>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)