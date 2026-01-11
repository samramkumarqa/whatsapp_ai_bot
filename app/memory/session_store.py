# Simple in-memory store (per WhatsApp number)
user_sessions = {}

def get_session(user_id: str) -> dict:
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "state": None,
            "order": {}
        }
    return user_sessions[user_id]

def reset_session(user_id: str):
    user_sessions[user_id] = {
        "state": None,
        "order": {}
    }