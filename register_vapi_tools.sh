#!/bin/bash
# Run this script ONCE after deploying to Railway.
# It registers all 7 tools in Vapi and prints the tool IDs.
# Then PATCH your assistant with all tool IDs (see patch_vapi_assistant.sh).

export VAPI_KEY="${VAPI_PUBLIC_KEY}"
RAILWAY_URL="${RAILWAY_URL:-https://YOUR-APP.up.railway.app}"

if [ -z "$VAPI_KEY" ]; then
  echo "ERROR: Set VAPI_PUBLIC_KEY environment variable first."
  exit 1
fi

echo "Registering tools against: $RAILWAY_URL"
echo ""

echo "--- Tool 1: lookup_customer_by_phone ---"
curl -s -X POST https://api.vapi.ai/tool \
  -H "Authorization: Bearer $VAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "function",
    "function": {
      "name": "lookup_customer_by_phone",
      "description": "Check if this caller is an existing Price Flooring customer. Always call this after getting the phone number.",
      "parameters": {
        "type": "object",
        "properties": {
          "phone_number": {"type": "string", "description": "Caller phone number, digits only"}
        },
        "required": ["phone_number"]
      }
    },
    "server": {"url": "'"$RAILWAY_URL"'/lookup-customer"}
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('ID:', d.get('id','ERROR'), '| Name:', d.get('function',{}).get('name','?'))"

echo ""
echo "--- Tool 2: save_customer ---"
curl -s -X POST https://api.vapi.ai/tool \
  -H "Authorization: Bearer $VAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "function",
    "function": {
      "name": "save_customer",
      "description": "Save or update a customer record with their contact and address info.",
      "parameters": {
        "type": "object",
        "properties": {
          "phone_number":  {"type": "string"},
          "first_name":    {"type": "string"},
          "last_name":     {"type": "string"},
          "email":         {"type": "string"},
          "address":       {"type": "string"},
          "notes":         {"type": "string"}
        },
        "required": ["phone_number"]
      }
    },
    "server": {"url": "'"$RAILWAY_URL"'/save-customer"}
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('ID:', d.get('id','ERROR'), '| Name:', d.get('function',{}).get('name','?'))"

echo ""
echo "--- Tool 3: create_lead ---"
curl -s -X POST https://api.vapi.ai/tool \
  -H "Authorization: Bearer $VAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "function",
    "function": {
      "name": "create_lead",
      "description": "Create a new lead record. MANDATORY — must be called before add_lead_details or confirm_appointment. Returns a lead_id needed for all subsequent steps.",
      "parameters": {
        "type": "object",
        "properties": {
          "phone_number":       {"type": "string"},
          "customer_name":      {"type": "string"},
          "email":              {"type": "string"},
          "property_address":   {"type": "string"},
          "project_type":       {"type": "string", "description": "e.g. hardwood installation, carpet, kitchen remodel, carpet binding"},
          "flooring_interest":  {"type": "string", "description": "e.g. engineered hardwood, LVP, porcelain tile"}
        },
        "required": ["phone_number", "customer_name"]
      }
    },
    "server": {"url": "'"$RAILWAY_URL"'/create-lead"}
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('ID:', d.get('id','ERROR'), '| Name:', d.get('function',{}).get('name','?'))"

echo ""
echo "--- Tool 4: add_lead_details ---"
curl -s -X POST https://api.vapi.ai/tool \
  -H "Authorization: Bearer $VAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "function",
    "function": {
      "name": "add_lead_details",
      "description": "Add project details to an existing lead. Call after create_lead.",
      "parameters": {
        "type": "object",
        "properties": {
          "lead_id":                    {"type": "integer"},
          "rooms_involved":             {"type": "string"},
          "approximate_sqft":           {"type": "integer"},
          "residential_or_commercial":  {"type": "string", "enum": ["residential", "commercial"]},
          "material_only_or_install":   {"type": "string", "enum": ["material only", "installation", "unsure"]},
          "timeline":                   {"type": "string"},
          "budget_range":               {"type": "string"},
          "preferred_callback":         {"type": "string"},
          "notes":                      {"type": "string"}
        },
        "required": ["lead_id"]
      }
    },
    "server": {"url": "'"$RAILWAY_URL"'/add-lead-details"}
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('ID:', d.get('id','ERROR'), '| Name:', d.get('function',{}).get('name','?'))"

echo ""
echo "--- Tool 5: get_available_slots ---"
curl -s -X POST https://api.vapi.ai/tool \
  -H "Authorization: Bearer $VAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "function",
    "function": {
      "name": "get_available_slots",
      "description": "Get available appointment slots for an estimate or consultation.",
      "parameters": {
        "type": "object",
        "properties": {
          "preferred_date":     {"type": "string", "description": "YYYY-MM-DD format, optional"},
          "appointment_type":   {"type": "string", "enum": ["estimate", "consultation", "design"], "description": "Type of appointment"}
        }
      }
    },
    "server": {"url": "'"$RAILWAY_URL"'/get-available-slots"}
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('ID:', d.get('id','ERROR'), '| Name:', d.get('function',{}).get('name','?'))"

echo ""
echo "--- Tool 6: confirm_appointment ---"
curl -s -X POST https://api.vapi.ai/tool \
  -H "Authorization: Bearer $VAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "function",
    "function": {
      "name": "confirm_appointment",
      "description": "Book an appointment and return a confirmation number.",
      "parameters": {
        "type": "object",
        "properties": {
          "lead_id":          {"type": "integer"},
          "slot_id":          {"type": "integer", "description": "From get_available_slots, optional"},
          "customer_name":    {"type": "string"},
          "phone_number":     {"type": "string"},
          "appointment_type": {"type": "string"},
          "preferred_date":   {"type": "string"},
          "preferred_time":   {"type": "string"},
          "notes":            {"type": "string"}
        },
        "required": ["lead_id", "customer_name", "phone_number"]
      }
    },
    "server": {"url": "'"$RAILWAY_URL"'/confirm-appointment"}
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('ID:', d.get('id','ERROR'), '| Name:', d.get('function',{}).get('name','?'))"

echo ""
echo "--- Tool 7: check_store_status ---"
curl -s -X POST https://api.vapi.ai/tool \
  -H "Authorization: Bearer $VAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "function",
    "function": {
      "name": "check_store_status",
      "description": "Check if Price Flooring is currently open or closed. Call this early in every conversation.",
      "parameters": {
        "type": "object",
        "properties": {}
      }
    },
    "server": {"url": "'"$RAILWAY_URL"'/check-store-status"}
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('ID:', d.get('id','ERROR'), '| Name:', d.get('function',{}).get('name','?'))"

echo ""
echo "Done. Copy the 7 tool IDs above and paste them into patch_vapi_assistant.sh"
