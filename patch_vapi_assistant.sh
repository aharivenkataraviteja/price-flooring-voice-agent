#!/bin/bash
# Run this AFTER register_vapi_tools.sh.
# Patches the Vapi assistant with the full system prompt and all 7 tool IDs.
# ALWAYS send the complete model object — partial PATCH wipes toolIds.

export VAPI_KEY="${VAPI_PUBLIC_KEY}"
ASSISTANT_ID="${VAPI_ASSISTANT_ID}"

if [ -z "$VAPI_KEY" ] || [ -z "$ASSISTANT_ID" ]; then
  echo "ERROR: Set VAPI_PUBLIC_KEY and VAPI_ASSISTANT_ID first."
  exit 1
fi

# ── Replace these with real IDs from register_vapi_tools.sh output ────────────
TOOL_ID_1="REPLACE_lookup_customer_by_phone"
TOOL_ID_2="REPLACE_save_customer"
TOOL_ID_3="REPLACE_create_lead"
TOOL_ID_4="REPLACE_add_lead_details"
TOOL_ID_5="REPLACE_get_available_slots"
TOOL_ID_6="REPLACE_confirm_appointment"
TOOL_ID_7="REPLACE_check_store_status"
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT=$(cat vapi_system_prompt.txt)

cat > /tmp/pf_vapi_payload.json << PAYLOAD
{
  "firstMessage": "Thanks for calling Price Flooring in Delray Beach. This is the virtual assistant. I can help with flooring options, estimates, design consultations, store hours, or connect you with the team. What can I help you with today?",
  "firstMessageMode": "assistant-speaks-first",
  "model": {
    "provider": "openai",
    "model": "gpt-4.1",
    "messages": [
      {
        "role": "system",
        "content": $(echo "$SYSTEM_PROMPT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")
      }
    ],
    "toolIds": [
      "$TOOL_ID_1",
      "$TOOL_ID_2",
      "$TOOL_ID_3",
      "$TOOL_ID_4",
      "$TOOL_ID_5",
      "$TOOL_ID_6",
      "$TOOL_ID_7"
    ]
  }
}
PAYLOAD

echo "Patching assistant $ASSISTANT_ID ..."
curl -s -X PATCH "https://api.vapi.ai/assistant/$ASSISTANT_ID" \
  -H "Authorization: Bearer $VAPI_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @/tmp/pf_vapi_payload.json \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK — assistant id:', d.get('id','ERROR'))"

echo ""
echo "Done. Attach the Vapi phone number to this assistant in the Vapi dashboard."
