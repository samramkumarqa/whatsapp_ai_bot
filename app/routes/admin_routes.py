from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from app.security.admin_auth import admin_auth
from app.services.database import (
    get_connection,
    update_order_status,
    get_order_by_id
)
from app.services.whatsapp import send_whatsapp_message
import os

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(admin_auth)]  # 🔒 PROTECT ALL ROUTES
)

ALLOWED_STATUSES = ["NEW", "PREPARING", "DELIVERED"]

@router.get("", dependencies=[Depends(admin_auth)])
def admin_dashboard():
    return FileResponse("app/static/dashboard.html")


@router.get("/orders", dependencies=[Depends(admin_auth)])
def get_orders():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            o.id,
            o.phone,
            o.subtotal,
            o.delivery,
            o.total,
            o.status,
            o.created_at,
            i.item,
            i.quantity,
            i.price,
            i.subtotal
        FROM orders o
        JOIN order_items i ON o.id = i.order_id
        ORDER BY o.created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    orders = {}

    for r in rows:
        order_id = r[0]

        if order_id not in orders:
            orders[order_id] = {
                "id": r[0],
                "phone": r[1],
                "subtotal": r[2],
                "delivery": r[3],
                "total": r[4],
                "status": r[5],
                "created_at": r[6],
                "items": []
            }

        orders[order_id]["items"].append({
            "item": r[7],
            "quantity": r[8],
            "price": r[9],
            "subtotal": r[10]
        })

    return list(orders.values())


@router.patch("/orders/{order_id}", dependencies=[Depends(admin_auth)])
def change_status(order_id: int, status: str):
    if status not in ALLOWED_STATUSES:
        return {"error": "Invalid status"}

    # 1️⃣ Update DB
    update_order_status(order_id, status)

    # 2️⃣ Fetch order
    order = get_order_by_id(order_id)
    if not order:
        return {"error": "Order not found"}

    # 3️⃣ Fetch items for this order
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT item, quantity
        FROM order_items
        WHERE order_id = ?
    """, (order_id,))

    items = cursor.fetchall()
    conn.close()

    # 4️⃣ Build items text
    items_text = "\n".join(
        f"- {item.title()} x {qty}"
        for item, qty in items
    )

    # 5️⃣ Build WhatsApp message
    if status == "PREPARING":
        msg = (
            f"🍳 *Order Update*\n\n"
            f"Your order #{order_id} is being prepared.\n\n"
            f"{items_text}"
        )
    elif status == "DELIVERED":
        msg = (
            f"🚚 *Order Delivered*\n\n"
            f"Your order #{order_id} has been delivered.\n\n"
            f"{items_text}\n\n"
            f"Thank you for ordering with us 🙏"
        )
    else:
        msg = None

    # 6️⃣ Send WhatsApp
    if msg:
        send_whatsapp_message(order["phone"], msg)

    return {"status": "updated"}

