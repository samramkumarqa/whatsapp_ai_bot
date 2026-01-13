def detect_intent(message: str) -> str:
    msg = message.lower().strip()

    if msg in ["hi", "hello", "hey"]:
        return "greeting"

    if msg in ["menu", "items", "price list"]:
        return "menu"

    if msg in ["delivery", "shipping"]:
        return "delivery"

    if msg in ["order", "buy", "purchase"]:
        return "order"

    if msg in ["agent", "human", "support"]:
        return "human"

    return "unknown"
