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
TOOL_ID_1="7a850875-c774-467e-88cc-5c79168dc6f0"
TOOL_ID_2="f4f4e28b-e50c-4edf-8b71-4fa8cc0d056a"
TOOL_ID_3="af73417c-b5ed-4323-98a0-2e440b1ccfb9"
TOOL_ID_4="122d934c-f959-4433-8db9-13bed1c40c37"
TOOL_ID_5="e23ce31c-6060-4443-89a5-69edd530fe15"
TOOL_ID_6="41495de3-5172-4b93-b9bb-ef86f151e092"
TOOL_ID_7="936ff9a2-664a-479e-aa27-c0ff6effb2be"
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
