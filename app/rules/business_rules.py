from app.rules.intents import detect_intent
from app.memory.session_store import get_session, reset_session
from app.services.database import save_order

MENU_ITEMS = ["tea", "coffee", "green tea"]
MENU_PRICES = {
    "tea": 50,
    "coffee": 70,
    "green tea": 80
}

DELIVERY_CHARGE = 50
FREE_DELIVERY_MIN = 500


def apply_business_rules(message: str, user_id: str) -> str | None:
    msg = message.lower().strip()
    session = get_session(user_id)
    intent = detect_intent(msg)

    # 🔁 ACTIVE ORDER FLOW
    if session["state"] == "ORDER_ITEM":
        if msg in MENU_ITEMS:
            session["order"]["item"] = msg
            session["state"] = "ORDER_QTY"
            return f"How many *{msg.title()}* would you like?"

        return "Please choose a valid item: Tea, Coffee, Green Tea."

    if session["state"] == "ORDER_QTY":
        if msg.isdigit() and int(msg) > 0:
            session["order"]["qty"] = int(msg)
            session["state"] = "CONFIRM"

            item = session["order"]["item"]
            qty = session["order"]["qty"]
            price = MENU_PRICES[item]
            subtotal = price * qty
            delivery_fee = 0 if subtotal >= FREE_DELIVERY_MIN else DELIVERY_CHARGE
            total = subtotal + delivery_fee

            # store calculation for confirm step
            session["order"].update({
                "price": price,
                "subtotal": subtotal,
                "delivery": delivery_fee,
                "total": total
            })

            return (
                f"🧾 *Confirm Order*\n"
                f"Item: {item.title()}\n"
                f"Quantity: {qty}\n"
                f"Price: ₹{price} each\n\n"
                f"Subtotal: ₹{subtotal}\n"
                f"Delivery: {'FREE' if delivery_fee == 0 else f'₹{delivery_fee}'}\n"
                f"*Total: ₹{total}*\n\n"
                f"Reply *Yes* to confirm or *No* to cancel."
            )

        return "Please enter a valid quantity."

    if session["state"] == "CONFIRM":
        if msg in ["yes", "y"]:
            order = session["order"]

            # 💾 SAVE TO DATABASE
            print("💾 CALLING save_order() with:", user_id, order)
            
            save_order(
                phone=user_id,
                item=order["item"],
                quantity=order["qty"],
                price=order["price"],
                subtotal=order["subtotal"],
                delivery=order["delivery"],
                total=order["total"]
            )

            reset_session(user_id)

            return (
                f"✅ *Order Placed Successfully!*\n\n"
                f"Item: {order['item'].title()}\n"
                f"Quantity: {order['qty']}\n"
                f"*Total Paid: ₹{order['total']}*\n\n"
                f"🙏 Thank you for ordering with us!"
            )

        if msg in ["no", "n"]:
            reset_session(user_id)
            return "❌ Order cancelled."

        return "Please reply *Yes* or *No*."

    # 🆕 START ORDER
    if intent == "order":
        session["state"] = "ORDER_ITEM"
        return "🛒 What item would you like to order?\nTea / Coffee / Green Tea"

    # 🧠 STATIC RULES
    if intent == "greeting":
        return "Hello 👋 How can I help you today?"

    if intent == "delivery":
        return (
            "🚚 *Delivery Info*\n"
            "Orders above ₹500 → FREE\n"
            "Below ₹500 → ₹50"
        )

    return None