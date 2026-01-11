from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.services.database import (
    get_connection,
    update_order_status,
    get_order_by_id,
)
from app.services.whatsapp import send_whatsapp_message
import os

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

ALLOWED_STATUSES = ["NEW", "PREPARING", "DELIVERED"]


# ---------------- DASHBOARD ----------------
@router.get("/")
def admin_dashboard():
    return FileResponse(
        os.path.join("app", "static", "dashboard.html")
    )


# ---------------- GET ORDERS ----------------
@router.get("/orders")
def get_orders():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, phone, item, quantity, subtotal, delivery, total, status, created_at
        FROM orders
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "phone": r[1],
            "item": r[2],
            "quantity": r[3],
            "subtotal": r[4],
            "delivery": r[5],
            "total": r[6],
            "status": r[7],
            "created_at": r[8],
        }
        for r in rows
    ]


# ---------------- UPDATE STATUS ----------------
@router.patch("/orders/{order_id}")
def change_status(order_id: int, status: str):
    status = status.upper()

    if status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed: {ALLOWED_STATUSES}"
        )

    update_order_status(order_id, status)
    order = get_order_by_id(order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if status == "PREPARING":
        msg = (
            f"🍳 *Order Update*\n\n"
            f"Your order for *{order['item'].title()}* is now being prepared."
        )
    elif status == "DELIVERED":
        msg = (
            f"🚚 *Order Delivered!*\n\n"
            f"Your order for *{order['item'].title()}* has been delivered.\n"
            f"🙏 Thank you for ordering with us!"
        )
    else:
        msg = None

    if msg:
        send_whatsapp_message(order["phone"], msg)

    return {"message": "Order status updated"}
