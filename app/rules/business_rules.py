from app.rules.intents import detect_intent
from app.memory.session_store import get_session, reset_session
from app.services.database import save_order
from app.services.database import create_order, add_order_item
from app.memory.session_store import reset_session

print("🔥 MULTI-ITEM BUSINESS RULES LOADED")

MENU_ITEMS = ["tea", "coffee", "green tea"]
MENU_PRICES = {
    "tea": 50,
    "coffee": 70,
    "green tea": 80
}

DELIVERY_CHARGE = 50
FREE_DELIVERY_MIN = 500

ORDER_ITEM = "ORDER_ITEM"
ORDER_QTY = "ORDER_QTY"
ADD_MORE = "ADD_MORE"
CONFIRM = "CONFIRM"


def apply_business_rules(message: str, user_id: str):
    msg = message.lower().strip()
    session = get_session(user_id)

    # ✅ HARD SAFETY: always ensure items list exists
    if "order" not in session:
        session["order"] = {"items": []}
    if "items" not in session["order"]:
        session["order"]["items"] = []

    print("🧠 CURRENT STATE:", session["state"])
    print("📦 CURRENT ITEMS:", session["order"]["items"])

    # 🔒 Detect intent ONLY if no active state
    intent = detect_intent(msg) if session["state"] is None else None

    # =========================
    # 🔁 MULTI-ITEM ORDER FLOW
    # =========================

    if session["state"] == ORDER_ITEM:
        if msg in MENU_ITEMS:
            session["current_item"] = msg
            session["state"] = ORDER_QTY
            return f"How many *{msg.title()}* would you like?"

        return "Please choose a valid item:\nTea / Coffee / Green Tea"

    if session["state"] == ORDER_QTY:
        if msg.isdigit() and int(msg) > 0:
            qty = int(msg)
            item = session["current_item"]
            price = MENU_PRICES[item]

            session["order"]["items"].append({
                "item": item,
                "qty": qty,
                "price": price,
                "subtotal": price * qty
            })

            session.pop("current_item", None)
            session["state"] = ADD_MORE

            return "➕ Anything else? (Yes / No)"

        return "Please enter a valid quantity."

    if session["state"] == ADD_MORE:
        if msg in ["yes", "y"]:
            session["state"] = ORDER_ITEM
            return "What else would you like?"

        if msg in ["no", "n"]:
            total = sum(i["subtotal"] for i in session["order"]["items"])
            delivery = 0 if total >= FREE_DELIVERY_MIN else DELIVERY_CHARGE
            grand_total = total + delivery

            session["order"].update({
                "total": total,
                "delivery": delivery,
                "grand_total": grand_total
            })

            session["state"] = CONFIRM

            summary = "\n".join(
                f"{i['item'].title()} x {i['qty']} = ₹{i['subtotal']}"
                for i in session["order"]["items"]
            )

            return (
                f"🧾 *Order Summary*\n\n"
                f"{summary}\n\n"
                f"Subtotal: ₹{total}\n"
                f"Delivery: {'FREE' if delivery == 0 else f'₹{delivery}'}\n"
                f"*Total: ₹{grand_total}*\n\n"
                f"Reply *Yes* to confirm or *No* to cancel."
            )

        return "Please reply Yes or No."

    if session["state"] == CONFIRM:
        if msg in ["yes", "y"]:
            order = session["order"]

            # 1️⃣ Create ONE order
            order_id = create_order(
                phone=user_id,
                subtotal=order["total"],
                delivery=order["delivery"],
                total=order["grand_total"]
            )

            # 2️⃣ Add multiple items
            for item in order["items"]:
                add_order_item(
                    order_id=order_id,
                    item=item["item"],
                    quantity=item["qty"],
                    price=item["price"],
                    subtotal=item["subtotal"]
                )

            # 3️⃣ Reset session
            reset_session(user_id)

            return "✅ *Order placed successfully!* 🎉"


        if msg in ["no", "n"]:
            reset_session(user_id)
            return "❌ Order cancelled."

        return "Please reply *Yes* or *No*."

    # =========================
    # 🆕 START ORDER
    # =========================

    if intent == "order":
        session["state"] = ORDER_ITEM
        session["order"] = {"items": []}
        return "🛒 What item would you like to order?\nTea / Coffee / Green Tea"

    # =========================
    # ℹ️ STATIC RESPONSES
    # =========================

    if intent == "greeting":
        return "Hello 👋 How can I help you today?"

    if intent == "delivery":
        return (
            "🚚 *Delivery Info*\n"
            "Orders above ₹500 → FREE\n"
            "Below ₹500 → ₹50"
        )

    return None
