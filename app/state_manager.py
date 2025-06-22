# app/state_manager.py

# In-memory store for user conversation states.
# Key: User's WhatsApp number (e.g., 'whatsapp:+27820000000')
# Value: A dictionary like {'state': 'awaiting_name', 'data': {}}
user_states = {}

def get_user_state(user_id):
    """Gets the current state for a user."""
    return user_states.get(user_id, {'state': None, 'data': {}})

def set_user_state(user_id, new_state, data=None):
    """Sets a new state for a user."""
    if data is None:
        data = {}
    user_states[user_id] = {'state': new_state, 'data': data}
    print(f"State for {user_id} set to {new_state}") # For debugging

def clear_user_state(user_id):
    """Clears the state for a user."""
    if user_id in user_states:
        del user_states[user_id]
        print(f"State for {user_id} cleared.") # For debugging