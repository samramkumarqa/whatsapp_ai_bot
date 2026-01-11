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

@router.patch("/orders/{order_id}", dependencies=[Depends(admin_auth)])
def change_status(order_id: int, status: str):
    if status not in ALLOWED_STATUSES:
        return {"error": "Invalid status"}

    update_order_status(order_id, status)
    order = get_order_by_id(order_id)

    if order:
        if status == "PREPARING":
            msg = f"🍳 Your *{order['item'].title()}* is being prepared."
        elif status == "DELIVERED":
            msg = f"🚚 Your *{order['item'].title()}* has been delivered. Thank you!"

        if msg:
            send_whatsapp_message(order["phone"], msg)

    return {"status": "updated"}
