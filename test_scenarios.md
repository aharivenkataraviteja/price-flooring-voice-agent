# Price Flooring Voice Agent — Test Scenarios

---

## Scenario 1 — New Flooring Estimate (Happy Path)

**Caller:** New caller, wants LVP in living room and kitchen.

**Expected flow:**
1. Agent opens with the greeting
2. Calls `check_store_status` — store is open
3. Asks for phone number → `lookup_customer_by_phone` → not found
4. Collects name, email, address → `save_customer`
5. `create_lead` (project_type: LVP installation)
6. Asks about rooms, sqft, current flooring, timeline — 1-2 questions at a time
7. `add_lead_details`
8. `get_available_slots` → offers 2-3 options
9. `confirm_appointment` → reads back confirmation number
10. Closes warmly

**Pass criteria:**
- Never quotes a price
- Collects all required fields
- Confirmation number returned and read to caller
- No filler phrases like "Great choice!"

---

## Scenario 2 — Returning Customer

**Caller:** Has called before. Phone number is in the database.

**Expected flow:**
1. Agent greets, calls `check_store_status`
2. Gets phone number → `lookup_customer_by_phone` → found
3. Says "Welcome back, [first name]! Is this still for [address]?"
4. Confirms or updates address
5. Still calls `create_lead` for new project (does NOT reuse old lead)
6. Proceeds normally

**Pass criteria:**
- Greeted by name
- New lead created (not reusing old lead_id)
- Address confirmed before assuming it's the same

---

## Scenario 3 — After-Hours Lead Capture

**Caller:** Calls at 9 PM on a Wednesday.

**Expected flow:**
1. Greeting, then `check_store_status` → is_open = false
2. Agent says we're closed, gives next open time (Thursday 8:30 AM)
3. Offers to take info for next-business-day callback
4. Runs lead capture (name, phone, address, project type, details)
5. Does NOT call `get_available_slots` or `confirm_appointment`
6. Asks preferred callback window (morning/afternoon)
7. Saves in `preferred_callback`

**Pass criteria:**
- Does NOT promise same-day callback
- Does NOT attempt to book a slot
- Lead fully saved with preferred callback time

---

## Scenario 4 — Spam / Solicitation Call

**Caller:** "Hi, I'm calling about SEO services for your website."

**Expected flow:**
1. Agent responds with exactly ONE line:
   "We're not looking for that right now — thanks for calling!"
2. Ends the call immediately

**Pass criteria:**
- No more than one sentence
- No collecting information
- Call ends

---

## Scenario 5 — Caller Asks for Team Member by Name

**Caller:** "Can I speak to Ray?"

**Expected flow:**
1. Agent says: "Let me try to connect you."
2. Transfers to (561) 327-4903

**Pass criteria:**
- Transfer happens immediately
- No attempt to take a message or collect lead details first
  (unless after hours — then offer callback message)

---

## Scenario 6 — Caller Demands Exact Price

**Caller:** "Just tell me how much it costs per square foot for hardwood."

**First response from agent:**
"Pricing depends on the material, square footage, and the scope of the project.
Our estimator gives you an exact number during the free visit — there's no obligation."

**Caller pushes again:** "Come on, just give me a ballpark."

**Second response:**
Agent tries once more to redirect: "I really can't give accurate numbers without
knowing the details — it varies a lot. But the estimate is free and the team will
have exact pricing for you."

**If caller pushes a third time:**
→ TRANSFER: "Let me connect you with someone on the team who can help."

**Pass criteria:**
- Never quotes a price at any point
- Transfers after persistent pushing

---

## Scenario 7 — Existing Order Status

**Caller:** "I had carpet installed last week and I'm calling about my order."

**Expected flow:**
1. Agent recognizes this as an existing order inquiry
2. Immediately says: "For order and installation questions, let me connect you
   with someone on the team directly."
3. Transfers to (561) 327-4903

**Pass criteria:**
- No lead capture attempted
- Transferred in 1-2 sentences

---

## Scenario 8 — Kitchen Remodel Inquiry

**Caller:** "I want to redo my whole kitchen — new cabinets, countertops, flooring."

**Expected flow:**
1. Collects basic info (name, phone, address)
2. Creates lead with project_type = "kitchen remodel"
3. Gets rough scope (timeline, rough budget if offered)
4. Says: "Full kitchen remodels are handled by our design team directly.
   I'll get your info to them and they'll reach out to set up a design consultation."
5. Saves preferred_callback time
6. Does NOT attempt to book a regular estimate slot

**Pass criteria:**
- Recognized as remodel (not standard flooring estimate)
- Lead saved correctly
- No slot booking attempted for large remodel

---

## Scenario 9 — Caller Doesn't Know Square Footage

**Caller:** "I have no idea how big the room is."

**Expected agent response:**
"No problem at all — our estimator will measure everything when they come out.
Do you know roughly how many rooms you're looking to do?"

**Pass criteria:**
- Does NOT get stuck on the sqft question
- Moves on naturally
- Saves approximate_sqft as null

---

## Scenario 10 — Product Comparison Question (No Purchase Intent Yet)

**Caller:** "What's the difference between LVP and hardwood?"

**Expected flow:**
1. Agent answers the question conversationally (using knowledge in system prompt)
2. Pivots naturally: "The best way to see the options is to come by the showroom
   or have our estimator bring samples to your home. Would you like to set that up?"
3. If caller says yes → run standard lead capture
4. If caller says no (just exploring) → thanks them, gives hours and address

**Pass criteria:**
- Correct general information given
- Pivot to consultation offered naturally
- No pricing quoted

---

## Scenario 11 — Complaint Call

**Caller:** "Your installer left a mess and scratched my baseboards!"

**Expected flow:**
1. Agent empathizes immediately: "I'm really sorry to hear that —
   let me get you over to someone on the team right away."
2. Transfers immediately to (561) 327-4903

**Pass criteria:**
- Does NOT argue or ask for details
- Transfers in one sentence after brief empathy
- No lead capture attempted

---

## Scenario 12 — Caller Asks to Speak to a Real Person

**First time:** "Can I talk to a real person?"

Agent: "Of course — let me connect you." → Transfer.

**If agent tries once more and caller repeats:**
→ Transfer immediately without asking again.

**Pass criteria:**
- No resistance or trying to handle it themselves
- Clean transfer

---

## Fallback Responses

| Situation | Expected Response |
|-----------|------------------|
| Caller mumbles / unclear | "Sorry, I didn't catch that — could you say that again?" |
| Tool times out | "Bear with me just one moment." then retry once |
| Tool returns error | Don't say "error" — say "Let me note that and have the team follow up." |
| Caller asks something completely off-topic | "I can help with flooring, remodeling, or connecting you with the team. What can I help you with?" |
| Caller is silent for 5+ seconds | "Are you still there?" |
| Caller hangs up before lead is saved | Whatever was captured is saved via partial tool calls already made |

---

## Transfer Rules Summary

| Trigger | Action |
|---------|--------|
| Asks for Ray, Nicole, Peter, Lucien, Kim | Transfer |
| Asks for manager or owner | Transfer |
| Asks for sales rep | Transfer |
| Exact pricing demand (after 2 redirects) | Transfer |
| Existing order or install status | Transfer |
| Complaint | Transfer |
| Financing approval/details | Transfer |
| Commercial project | Transfer |
| Large kitchen or bath remodel | Transfer |
| Angry or confused caller | Transfer |
| "I want to speak to a real person" (2nd time) | Transfer |

Transfer number: **(561) 327-4903**
Transfer script: "Let me connect you with someone on the team."
