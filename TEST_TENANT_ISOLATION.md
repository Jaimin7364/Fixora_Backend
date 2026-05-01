# Tenant Isolation Testing Guide

Follow this step-by-step to test multi-tenant isolation between Organization Alpha and Organization Beta.

## Prerequisites
- Backend server running locally
- Database initialized with migration

## Quick Start (5 minutes)

### Step 1: Create 2 Organizations with Test Users

```bash
cd backend
python test_setup_tenants.py
```

Output will show:
```
✅ Created Organization: Alpha Corp (id=1)
✅ Created Organization: Beta Industries (id=2)
✅ Created user: alpha_admin@test.com in Alpha Corp
✅ Created user: beta_admin@test.com in Beta Industries
```

Save these credentials:
- **Alpha**: email=`alpha_admin@test.com`, password=`TestPassword123`
- **Beta**: email=`beta_admin@test.com`, password=`TestPassword123`

### Step 2: Start Backend Server

```bash
# In another terminal
cd backend
uvicorn app.main:app --reload
```

### Step 3: Run Tenant Isolation Test Script

```bash
# Make script executable
chmod +x test_tenant_isolation.sh

# Run the test
./test_tenant_isolation.sh
```

Expected output shows all tests passing:
```
Step 1: Logging in to both organizations...
✅ Alpha Admin Token: eyJ0eXAiOiJKV1QiLi...
✅ Beta Admin Token: eyJ0eXAiOiJKV1QiLi...

Step 2: Creating ticket in Alpha organization...
✅ Created ticket in Alpha: TKT-2026-0001 (id=1)

Step 3: Creating ticket in Beta organization...
✅ Created ticket in Beta: TKT-2026-0002 (id=2)

Step 4: POSITIVE TEST - Alpha lists tickets (should see own ticket)...
✅ PASS: Alpha can see its own ticket

Step 5: NEGATIVE TEST - Beta tries to list tickets (must NOT see Alpha ticket)...
✅ PASS: Beta cannot see Alpha ticket

Step 6: NEGATIVE TEST - Beta tries to fetch Alpha ticket by ID...
✅ PASS: Beta gets 404 when trying to access Alpha ticket

... (more tests) ...

✅ PASS: Each org sees only its own ticket in metrics
```

## Manual Testing (if you prefer curl)

### Login Alpha

```bash
ALPHA_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alpha_admin@test.com&password=TestPassword123" | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token: $ALPHA_TOKEN"
```

### Login Beta

```bash
BETA_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=beta_admin@test.com&password=TestPassword123" | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token: $BETA_TOKEN"
```

### Create Ticket in Alpha

```bash
curl -X POST http://localhost:8000/api/v1/tickets/ \
  -H "Authorization: Bearer $ALPHA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Alpha Laptop Issue",
    "description": "Screen freezing",
    "category": "hardware"
  }'
```

### Alpha Lists Its Tickets (should see the ticket)

```bash
curl http://localhost:8000/api/v1/tickets/ \
  -H "Authorization: Bearer $ALPHA_TOKEN"
```

### Beta Lists Tickets (should NOT see Alpha ticket)

```bash
curl http://localhost:8000/api/v1/tickets/ \
  -H "Authorization: Bearer $BETA_TOKEN"
```

If Beta result is empty `{"tickets": [], "total": 0, ...}`, isolation is working ✅

### Beta Tries to Get Alpha Ticket by ID (should fail)

```bash
curl http://localhost:8000/api/v1/tickets/1 \
  -H "Authorization: Bearer $BETA_TOKEN"
```

Expected response:
```json
{
  "detail": "Ticket with ID 1 not found"
}
```

If you get this instead:
```json
{
  "detail": "You do not have permission to view this ticket"
}
```

Both are correct - it means isolation is working.

## What's Being Tested

| Test | Purpose | Expected Result |
|------|---------|-----------------|
| Alpha sees its own ticket | Positive case | ✅ PASS |
| Beta cannot see Alpha ticket in list | Isolation | ✅ PASS |
| Beta cannot get Alpha ticket by ID | Isolation | ✅ PASS |
| Beta sees its own ticket | Positive case | ✅ PASS |
| Alpha cannot see Beta ticket | Isolation | ✅ PASS |
| Alpha cannot get Beta ticket by ID | Isolation | ✅ PASS |
| Alpha metrics only count Alpha tickets | Analytics isolation | ✅ PASS |
| Beta metrics only count Beta tickets | Analytics isolation | ✅ PASS |

## If Tests Fail

1. **"Beta can see Alpha ticket"** → Organization scoping not working in ticket service
2. **"Beta cannot see its own ticket"** → User not properly linked to organization
3. **Metrics show combined counts** → Metrics endpoint not filtering by organization

Check:
- Database has `organization_id` assigned to tickets/users
- User model has `organization_id` field populated
- Ticket service filters by `organization_id` in queries
- API routes pass `current_user.organization_id` to services

## Database Check

```bash
# List organizations
sqlite3 fixora.db "SELECT id, name, slug FROM organizations;"

# List users with organization
sqlite3 fixora.db "SELECT id, email, organization_id FROM users;"

# List tickets with organization
sqlite3 fixora.db "SELECT id, ticket_number, organization_id FROM tickets;"
```

All should show `organization_id` populated.

## Next Steps

After confirming isolation works:
1. Commit changes to git
2. Push to deployed server
3. Run migration on production DB
4. Run RLS policy SQL on Postgres (for extra security layer)
