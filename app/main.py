from fastapi import FastAPI, Request
from app.rules.business_rules import apply_business_rules
from app.services.llm import get_llm_response
from app.services.whatsapp import send_whatsapp_message
from app.services.database import init_db
from app.routes.admin_routes import router as admin_router

# ✅ DEFINE app FIRST
app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_db()

# 🔒 ADMIN ROUTER (WITH AUTH)
app.include_router(admin_router)

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.form()
    incoming_msg = data.get("Body", "")
    from_number = data.get("From")

    print("Incoming WhatsApp message:", incoming_msg)

    reply = apply_business_rules(incoming_msg, from_number)

    if reply is None:
        reply = get_llm_response(incoming_msg)

    print("Reply:", reply)
    send_whatsapp_message(from_number, reply)

    return "OK"
