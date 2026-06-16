import json
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from database import init_db
from models import (
    LookupCustomerRequest, SaveCustomerRequest, CreateLeadRequest,
    AddLeadDetailsRequest, GetAvailableSlotsRequest, ConfirmAppointmentRequest,
    CheckStoreStatusRequest
)
import crud
from store_hours import get_store_status


# ── VapiToolMiddleware ────────────────────────────────────────────────────────

class VapiToolMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        body = b""
        more_body = True
        while more_body:
            message = await receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        vapi_tool_call_id = None
        if body:
            try:
                data = json.loads(body)
                msg = data.get("message", {})
                if msg.get("type") == "tool-calls" and "toolCallList" in msg:
                    tool_call = msg["toolCallList"][0]
                    vapi_tool_call_id = tool_call["id"]
                    args_str = tool_call["function"]["arguments"]
                    args = json.loads(args_str) if isinstance(args_str, str) else args_str
                    body = json.dumps(args).encode()
            except (json.JSONDecodeError, KeyError, IndexError):
                pass

        body_sent = False

        async def new_receive():
            nonlocal body_sent
            if not body_sent:
                body_sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.disconnect"}

        if vapi_tool_call_id is None:
            await self.app(scope, new_receive, send)
            return

        response_body = b""

        async def capture_send(message):
            nonlocal response_body
            if message["type"] == "http.response.body":
                response_body += message.get("body", b"")

        await self.app(scope, new_receive, capture_send)

        vapi_response = json.dumps({
            "results": [{"toolCallId": vapi_tool_call_id, "result": response_body.decode()}]
        }).encode()

        await send({"type": "http.response.start", "status": 200,
                    "headers": [[b"content-type", b"application/json"],
                                [b"content-length", str(len(vapi_response)).encode()]]})
        await send({"type": "http.response.body", "body": vapi_response, "more_body": False})


# ── App setup ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Price Flooring Voice Agent API", lifespan=lifespan)
app.add_middleware(VapiToolMiddleware)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/lookup-customer")
def lookup_customer(body: LookupCustomerRequest):
    customer = crud.get_customer_by_phone(body.phone_number)
    if customer:
        past = crud.get_conn()
        leads = past.execute(
            "SELECT project_type, flooring_interest, created_at FROM leads WHERE phone_number = ? ORDER BY created_at DESC LIMIT 3",
            (body.phone_number,)
        ).fetchall()
        past.close()
        return {
            "found": True,
            "first_name": customer.get("first_name"),
            "last_name": customer.get("last_name"),
            "email": customer.get("email"),
            "address": customer.get("address"),
            "past_projects": [dict(r) for r in leads]
        }
    return {"found": False}


@app.post("/save-customer")
def save_customer(body: SaveCustomerRequest):
    result = crud.upsert_customer(
        phone_number=body.phone_number,
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        address=body.address,
        notes=body.notes
    )
    return result


@app.post("/create-lead")
def create_lead(body: CreateLeadRequest):
    result = crud.create_lead(
        phone_number=body.phone_number,
        customer_name=body.customer_name,
        email=body.email,
        property_address=body.property_address,
        project_type=body.project_type,
        flooring_interest=body.flooring_interest
    )
    return result


@app.post("/add-lead-details")
def add_lead_details(body: AddLeadDetailsRequest):
    result = crud.update_lead_details(
        lead_id=body.lead_id,
        rooms_involved=body.rooms_involved,
        approximate_sqft=body.approximate_sqft,
        residential_or_commercial=body.residential_or_commercial,
        material_only_or_install=body.material_only_or_install,
        timeline=body.timeline,
        budget_range=body.budget_range,
        preferred_callback=body.preferred_callback,
        notes=body.notes
    )
    return result


@app.post("/get-available-slots")
def get_available_slots(body: GetAvailableSlotsRequest):
    slots = crud.get_available_slots(
        preferred_date=body.preferred_date,
        appointment_type=body.appointment_type or "estimate"
    )
    if not slots:
        return {
            "slots": [],
            "message": "No pre-scheduled slots available right now. We'll have the team reach out to confirm a time."
        }
    return {"slots": slots}


@app.post("/confirm-appointment")
def confirm_appointment(body: ConfirmAppointmentRequest):
    result = crud.confirm_appointment(
        lead_id=body.lead_id,
        slot_id=body.slot_id,
        customer_name=body.customer_name,
        phone_number=body.phone_number,
        appointment_type=body.appointment_type or "estimate",
        preferred_date=body.preferred_date,
        preferred_time=body.preferred_time,
        notes=body.notes
    )
    return result


@app.post("/check-store-status")
def check_store_status(body: CheckStoreStatusRequest):
    return get_store_status()


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    with open("dashboard.html") as f:
        return f.read()


@app.get("/api/leads")
def api_leads():
    return crud.get_leads(limit=100)


@app.get("/health")
def health():
    return {"status": "ok", "business": "Price Flooring"}
