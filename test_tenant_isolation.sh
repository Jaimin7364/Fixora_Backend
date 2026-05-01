#!/bin/bash

# Test tenant isolation between Alpha and Beta organizations
# Usage: bash test_tenant_isolation.sh

API_URL="http://localhost:8000/api/v1"

echo "========================================"
echo "Fixora Multi-Tenant Isolation Test"
echo "========================================"
echo ""

# Step 1: Login both organizations
echo "Step 1: Logging in to both organizations..."
echo ""

ALPHA_LOGIN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alpha_admin@test.com&password=TestPassword123")

ALPHA_TOKEN=$(echo $ALPHA_LOGIN | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "✅ Alpha Admin Token: ${ALPHA_TOKEN:0:20}..."

BETA_LOGIN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=beta_admin@test.com&password=TestPassword123")

BETA_TOKEN=$(echo $BETA_LOGIN | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "✅ Beta Admin Token: ${BETA_TOKEN:0:20}..."
echo ""

# Step 2: Create ticket in Alpha
echo "Step 2: Creating ticket in Alpha organization..."
ALPHA_TICKET=$(curl -s -X POST "$API_URL/tickets/" \
  -H "Authorization: Bearer $ALPHA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Alpha Ticket - Laptop Issue",
    "description": "Laptop screen keeps freezing in Alpha org",
    "category": "hardware"
  }')

ALPHA_TICKET_ID=$(echo $ALPHA_TICKET | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
ALPHA_TICKET_NUM=$(echo $ALPHA_TICKET | grep -o '"ticket_number":"[^"]*' | cut -d'"' -f4)
echo "✅ Created ticket in Alpha: $ALPHA_TICKET_NUM (id=$ALPHA_TICKET_ID)"
echo ""

# Step 3: Create ticket in Beta
echo "Step 3: Creating ticket in Beta organization..."
BETA_TICKET=$(curl -s -X POST "$API_URL/tickets/" \
  -H "Authorization: Bearer $BETA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Beta Ticket - Printer Problem",
    "description": "Printer not connecting in Beta org",
    "category": "printer"
  }')

BETA_TICKET_ID=$(echo $BETA_TICKET | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
BETA_TICKET_NUM=$(echo $BETA_TICKET | grep -o '"ticket_number":"[^"]*' | cut -d'"' -f4)
echo "✅ Created ticket in Beta: $BETA_TICKET_NUM (id=$BETA_TICKET_ID)"
echo ""

# Step 4: POSITIVE TEST - Alpha should see its own ticket
echo "Step 4: POSITIVE TEST - Alpha lists tickets (should see own ticket)..."
ALPHA_LIST=$(curl -s -X GET "$API_URL/tickets/?page=1&page_size=10" \
  -H "Authorization: Bearer $ALPHA_TOKEN")

if echo $ALPHA_LIST | grep -q "$ALPHA_TICKET_NUM"; then
  echo "✅ PASS: Alpha can see its own ticket"
else
  echo "❌ FAIL: Alpha cannot see its own ticket"
fi
echo ""

# Step 5: NEGATIVE TEST - Beta cannot see Alpha ticket
echo "Step 5: NEGATIVE TEST - Beta tries to list tickets (must NOT see Alpha ticket)..."
BETA_LIST=$(curl -s -X GET "$API_URL/tickets/?page=1&page_size=10" \
  -H "Authorization: Bearer $BETA_TOKEN")

if echo $BETA_LIST | grep -q "$ALPHA_TICKET_NUM"; then
  echo "❌ FAIL: Beta can see Alpha ticket (ISOLATION BROKEN!)"
else
  echo "✅ PASS: Beta cannot see Alpha ticket"
fi
echo ""

# Step 6: NEGATIVE TEST - Beta cannot get Alpha ticket by ID
echo "Step 6: NEGATIVE TEST - Beta tries to fetch Alpha ticket by ID..."
ALPHA_GET=$(curl -s -X GET "$API_URL/tickets/$ALPHA_TICKET_ID" \
  -H "Authorization: Bearer $BETA_TOKEN")

if echo $ALPHA_GET | grep -q "not found"; then
  echo "✅ PASS: Beta gets 404 when trying to access Alpha ticket"
elif echo $ALPHA_GET | grep -q "forbidden"; then
  echo "✅ PASS: Beta gets 403 when trying to access Alpha ticket"
else
  echo "❌ FAIL: Beta should not be able to access Alpha ticket"
fi
echo ""

# Step 7: POSITIVE TEST - Beta should see its own ticket
echo "Step 7: POSITIVE TEST - Beta should see its own ticket..."
if echo $BETA_LIST | grep -q "$BETA_TICKET_NUM"; then
  echo "✅ PASS: Beta can see its own ticket"
else
  echo "❌ FAIL: Beta cannot see its own ticket"
fi
echo ""

# Step 8: NEGATIVE TEST - Alpha cannot see Beta ticket
echo "Step 8: NEGATIVE TEST - Alpha tries to list tickets (must NOT see Beta ticket)..."
if echo $ALPHA_LIST | grep -q "$BETA_TICKET_NUM"; then
  echo "❌ FAIL: Alpha can see Beta ticket (ISOLATION BROKEN!)"
else
  echo "✅ PASS: Alpha cannot see Beta ticket"
fi
echo ""

# Step 9: NEGATIVE TEST - Alpha cannot get Beta ticket by ID
echo "Step 9: NEGATIVE TEST - Alpha tries to fetch Beta ticket by ID..."
BETA_GET=$(curl -s -X GET "$API_URL/tickets/$BETA_TICKET_ID" \
  -H "Authorization: Bearer $ALPHA_TOKEN")

if echo $BETA_GET | grep -q "not found"; then
  echo "✅ PASS: Alpha gets 404 when trying to access Beta ticket"
elif echo $BETA_GET | grep -q "forbidden"; then
  echo "✅ PASS: Alpha gets 403 when trying to access Beta ticket"
else
  echo "❌ FAIL: Alpha should not be able to access Beta ticket"
fi
echo ""

# Step 10: Test metrics isolation
echo "Step 10: METRICS TEST - Alpha metrics should not include Beta tickets..."
ALPHA_METRICS=$(curl -s -X GET "$API_URL/metrics/dashboard" \
  -H "Authorization: Bearer $ALPHA_TOKEN")

ALPHA_TOTAL=$(echo $ALPHA_METRICS | grep -o '"total_tickets":[0-9]*' | cut -d':' -f2)
echo "Alpha sees total_tickets: $ALPHA_TOTAL (should be 1)"

BETA_METRICS=$(curl -s -X GET "$API_URL/metrics/dashboard" \
  -H "Authorization: Bearer $BETA_TOKEN")

BETA_TOTAL=$(echo $BETA_METRICS | grep -o '"total_tickets":[0-9]*' | cut -d':' -f2)
echo "Beta sees total_tickets: $BETA_TOTAL (should be 1)"

if [ "$ALPHA_TOTAL" = "1" ] && [ "$BETA_TOTAL" = "1" ]; then
  echo "✅ PASS: Each org sees only its own ticket in metrics"
else
  echo "❌ FAIL: Metrics not properly isolated"
fi
echo ""

echo "========================================"
echo "TEST COMPLETE"
echo "========================================"
echo ""
echo "Summary:"
echo "- If all tests show ✅ PASS, tenant isolation is working!"
echo "- If any show ❌ FAIL, there's a security issue to fix."
