# Fixora Backend - Deployment Guide

## 🎯 Current Status

### ✅ Working:
- **n8n Classification Webhook**: `http://143.244.136.25:5678/webhook/classify-ticket`
- **Backend Health Check**: `http://143.244.136.25:8000/health`
- **FastAPI Server**: Running on port 8000

### ⚠️ Needs Verification:
- **Multi-tenant migration**: Backfill org IDs for existing data
- **Slack OAuth**: Install flow must be validated

## 🚀 Deployment Steps

### Step 1: SSH to Server

```bash
ssh user@143.244.136.25
```

### Step 2: Navigate to Backend Directory

```bash
cd /path/to/Fixora/backend
# Find the directory where your backend is deployed
```

### Step 3: Upload Initialization Files

Upload these files to your server:
- `init_database.py` - Database initialization script
- `WORKFLOW_DOCUMENTATION.md` - Complete workflow guide

You can use SCP from your local machine:

```bash
scp init_database.py user@143.244.136.25:/path/to/backend/
```

### Step 4: Run Database Initialization

On the server, run:

```bash
# Activate your virtual environment if using one
source venv/bin/activate  # or whatever your venv name is

# Run initialization
python3 init_database.py
```

**Expected Output:**
```
==================================================
Fixora Database Initialization
==================================================
Creating database tables...
✅ Tables created successfully

Initializing SLA policies...
✅ SLA policies created:
   - Low: 72 hours
   - Medium: 48 hours
   - High: 24 hours
   - Urgent: 8 hours

Creating sample users...
✅ Sample users created:
   - admin@fixora.com (Admin)
   - support@fixora.com (IT Support)
   - john.doe@fixora.com (Employee)
   - jane.smith@fixora.com (Employee)

==================================================
✅ Database initialization completed successfully!
==================================================
```

### Step 5: Run Multi-Tenant Backfill

```bash
python3 migrate_multitenancy.py
```

Expected output:
```
Migration complete:
  users updated: <n>
  memberships created: <n>
  tickets updated: <n>
```

### Step 6: Verify Deployment

Run the test script from your local machine:

```bash
bash test_backend.sh
```

You should see:
```
✅ ALL TESTS PASSED!
🎉 Backend is fully functional and ready for Slack bot integration!
```

## 🔧 Alternative: Direct SQL Initialization

If you prefer to run SQL directly on your PostgreSQL database:

```sql
-- Create SLA Policies
INSERT INTO sla_policies (priority, response_time_hours, resolution_time_hours, description) VALUES
('low', 24, 72, 'Low priority - 3 business days'),
('medium', 8, 48, 'Medium priority - 2 business days'),
('high', 4, 24, 'High priority - 24 hours'),
('urgent', 1, 8, 'Urgent priority - 8 hours');

-- Create a test user
INSERT INTO users (email, full_name, department, role, is_active) VALUES
('admin@fixora.com', 'Admin User', 'IT', 'admin', true);
```

## 📊 Database Connection

Your backend is currently using:
```
DATABASE_URL=postgresql://postgres.vydljldgrjggxqgsutwh:***@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres
```

Make sure this is correctly set in your `.env` file on the server.

## 🧪 Testing After Deployment

### Test 1: Create Ticket via API

```bash
curl -X POST http://143.244.136.25:8000/api/v1/tickets/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test ticket - Cannot login",
    "description": "User unable to login to system. Getting authentication error.",
    "category": "access",
    "user_id": 1
  }' | python3 -m json.tool
```

**Expected Response:**
```json
{
  "id": 1,
  "ticket_number": "TKT-2026-0001",
  "title": "Test ticket - Cannot login",
  "category": "access",
  "priority": "high",
  "status": "open",
  "ai_classification": "access_high",
  "ai_confidence": 0.9
}
```

### Test 2: List Tickets

```bash
curl http://143.244.136.25:8000/api/v1/tickets/ | python3 -m json.tool
```

### Test 3: Get Ticket by ID

```bash
curl http://143.244.136.25:8000/api/v1/tickets/1 | python3 -m json.tool
```

## 🤖 Slack OAuth + Bot Integration

### 1. Configure Slack OAuth
Set these in `.env`:

```
SLACK_CLIENT_ID=...
SLACK_CLIENT_SECRET=...
SLACK_OAUTH_REDIRECT_URI=https://your-domain.com/api/v1/slack/oauth/callback
SLACK_SIGNING_SECRET=...
SLACK_ENCRYPTION_KEY=...
```

### 2. Install App in Workspace
Open the install URL endpoint:

```
GET /api/v1/slack/oauth/install
```

Follow the `install_url` and complete the install. This stores the workspace mapping.

### 3. Slack Events/Commands
Configure Slack to send events and commands to:

```
POST /api/v1/slack/events
POST /api/v1/slack/commands
POST /api/v1/slack/interactions
```

Once the backend is working, you can integrate with your Slack bot:

### Endpoint for Creating Tickets:
```
POST http://143.244.136.25:8000/api/v1/tickets/
```

### Request Body:
```json
{
  "title": "Brief description of issue",
  "description": "Detailed description from user",
  "category": "software",
  "user_id": 1
}
```

### Response:
```json
{
  "id": 123,
  "ticket_number": "TKT-2026-0123",
  "status": "open",
  "category": "access",
  "priority": "high",
  "ai_classification": "access_high",
  "ai_confidence": 0.9
}
```

The Slack bot should:
1. Receive user message/command
2. Parse and format the request
3. Call backend API to create ticket
4. Backend automatically sends to n8n for AI classification
5. Return ticket number to user in Slack

## 📝 Notes

- **n8n workflow** is already configured and working
- **Backend server** is running but needs database initialization
- **SLA policies** are required for ticket creation (calculates deadlines)
- **User ID** defaults to 1 for now (implement auth later)
- **AI classification** happens automatically and updates the ticket

## 🔍 Troubleshooting

### Issue: Still getting 500 errors after initialization

Check backend logs:
```bash
# On server
journalctl -u backend-service -f
# or
pm2 logs backend
# or wherever your logs are
```

### Issue: Can't connect to database

Verify `.env` file on server contains correct DATABASE_URL

### Issue: n8n not classifying

Check n8n workflow is active at: `http://143.244.136.25:5678`

## ✅ Success Checklist

- [ ] SSH access to server works
- [ ] Backend directory located
- [ ] `init_database.py` uploaded to server
- [ ] Database initialized successfully
- [ ] Test script passes all tests
- [ ] Ticket creation works
- [ ] n8n classification updates ticket
- [ ] Ready for Slack bot integration

## 🎉 Next Steps After Deployment

1. ✅ Database initialized
2. ✅ Backend fully functional
3. 🔄 Integrate Slack bot
4. 🔄 Add authentication (JWT)
5. 🔄 Build admin dashboard
6. 🔄 Add email notifications
