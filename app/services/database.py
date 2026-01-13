import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, "orders.db")

print("🗄️ USING DATABASE:", DB_PATH)


def get_connection():
    return sqlite3.connect(DB_PATH)

def update_order_status(order_id, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders SET status = ?
        WHERE id = ?
    """, (status, order_id))

    conn.commit()
    conn.close()

def get_order_by_id(order_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, phone, item, status
        FROM orders WHERE id = ?
    """, (order_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "phone": row[1],
        "item": row[2],
        "status": row[3]
    }


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            item TEXT,
            quantity INTEGER,
            price INTEGER,
            subtotal INTEGER,
            delivery INTEGER,
            total INTEGER,
            status TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()



def save_order(phone, item, quantity, price, subtotal, delivery, total):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO orders
        (phone, item, quantity, price, subtotal, delivery, total, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        phone,
        item,
        quantity,
        price,
        subtotal,
        delivery,
        total,
        "NEW",
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()