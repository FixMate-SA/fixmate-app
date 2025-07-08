def send_whatsapp_message(to_number, message_body=None, audio_url=None, audio_id=None):
    print("--- Attempting to send WhatsApp message ---")

    # Get API key and URL from environment variables
    DIALOG_360_API_KEY = os.environ.get('DIALOG_360_API_KEY')
    DIALOG_360_URL = os.environ.get('DIALOG_360_URL')

    if not DIALOG_360_API_KEY:
        print("❌ API key not set.")
        return None

    if not DIALOG_360_URL:
        print("❌ DIALOG_360_URL not set.")
        return None

    headers = {
        "D360-API-KEY": DIALOG_360_API_KEY,
        "Content-Type": "application/json"
    }

    recipient_number = to_number.replace("whatsapp:+", "").replace("+", "").strip()

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_number
    }

    if message_body:
        payload["type"] = "text"
        payload["text"] = {"body": message_body}
    elif audio_url:
        payload["type"] = "audio"
        payload["audio"] = {"link": audio_url, "voice": True}
    elif audio_id:
        payload["type"] = "audio"
        payload["audio"] = {"id": audio_id, "voice": True}
    else:
        print("❌ ERROR: No valid content provided (text, audio_url, or audio_id).")
        return None

    print(f"🔁 Payload: {json.dumps(payload)}")

    try:
        response = requests.post(DIALOG_360_URL, headers=headers, json=payload)
        print(f"✅ HTTP Status Code: {response.status_code}")
        print(f"🔽 Response: {response.text}")

        response.raise_for_status()

        data = response.json()
        message_id = data.get("messages", [{}])[0].get("id", "N/A")
        print(f"✅ Message sent! ID: {message_id}")
        return message_id

    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR sending WhatsApp message: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                print("🔽 Error Details:", e.response.json())
            except:
                pass
        return None
