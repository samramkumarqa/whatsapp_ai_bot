def apply_business_rules(message: str):
    msg = message.lower()

    if "delivery" in msg and "free" in msg:
        return "Yes 👍 Orders above ₹500 qualify for free delivery. Orders below ₹500 have a delivery charge of ₹50."

    if "delivery charge" in msg:
        return "The delivery charge is ₹50 for orders below ₹500. Orders above ₹500 have free delivery."

    return None
