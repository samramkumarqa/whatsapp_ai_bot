def detect_intent(message: str) -> str:
    msg = message.lower()

    if any(word in msg for word in ["hi", "hello", "hey"]):
        return "greeting"

    if any(word in msg for word in ["menu", "items", "price list"]):
        return "menu"

    if any(word in msg for word in ["delivery", "shipping"]):
        return "delivery"

    if any(word in msg for word in ["order", "buy", "purchase"]):
        return "order"

    if any(word in msg for word in ["agent", "human", "support"]):
        return "human"

    return "unknown"
