# app/memory/session_store.py

user_sessions = {}

def create_session():
    return {
        "state": None,
        "order": {
            "items": []
        }
    }

def get_session(user_id: str):
    if user_id not in user_sessions:
        user_sessions[user_id] = create_session()
    return user_sessions[user_id]

def reset_session(user_id: str):
    user_sessions[user_id] = create_session()
