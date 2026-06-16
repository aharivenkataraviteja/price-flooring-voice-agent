#!/bin/bash
# List and optionally delete Vapi tools.
# Always verify IDs by listing first — never delete by guessing.

export VAPI_KEY="${VAPI_PUBLIC_KEY}"

if [ -z "$VAPI_KEY" ]; then
  echo "ERROR: Set VAPI_PUBLIC_KEY first."
  exit 1
fi

echo "=== Current Vapi tools ==="
curl -s -X GET https://api.vapi.ai/tool \
  -H "Authorization: Bearer $VAPI_KEY" \
  | python3 -c "
import sys, json
tools = json.load(sys.stdin)
for t in tools:
    print(f\"  {t.get('id')}  {t.get('function',{}).get('name','?')}\")"

echo ""
echo "To delete a tool, run:"
echo "  curl -X DELETE https://api.vapi.ai/tool/TOOL_ID -H 'Authorization: Bearer \$VAPI_PUBLIC_KEY'"
