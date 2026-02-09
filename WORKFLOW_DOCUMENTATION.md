# Fixora - Complete Workflow Documentation

## 🔄 System Architecture & Data Flow

```
┌─────────────┐
│  Slack Bot  │ (Employee creates ticket via Slack)
│  (User)     │
└──────┬──────┘
       │ POST /api/v1/tickets/
       ▼
┌─────────────────────────────┐
│   FastAPI Backend           │
│   (http://143.244.136.25:8000)│
│                             │
│  1. Create Ticket           │
│  2. Save to Database        │
│  3. Generate Ticket Number  │
│     (TKT-2026-0001)        │
└──────┬──────────────────────┘
       │
       │ HTTP POST
       ▼
┌─────────────────────────────────────────┐
│  n8n Workflow Engine                    │
│  (http://143.244.136.25:5678)          │
│                                         │
│  ┌──────────┐  ┌──────────────────┐   │
│  │ Webhook  │─>│ Prepare Input    │   │
│  └──────────┘  └────────┬─────────┘   │
│                         │              │
│                         ▼              │
│              ┌──────────────────┐      │
│              │ Call Gemini AI   │      │
│              └────────┬─────────┘      │
│                       │                │
│                       ▼                │
│              ┌──────────────────┐      │
│              │ Parse Response   │      │
│              └────────┬─────────┘      │
│                       │                │
│                       ▼                │
│              ┌──────────────────┐      │
│              │ Send Response    │      │
│              └────────┬─────────┘      │
└────────────────────────┼───────────────┘
                        │
        ┌───────────────┴────────────────┐
        │ Classification Response:        │
        │ {                              │
        │   category: "access",          │
        │   priority: "high",            │
        │   confidence: "high",          │
        │   suggested_team: "IAM"        │
        │ }                              │
        └───────────────┬────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   FastAPI Backend             │
        │   Receives & Processes:       │
        │   - Update ticket category    │
        │   - Update ticket priority    │
        │   - Set AI confidence score   │
        │   - Recalculate SLA deadline  │
        └───────────────┬───────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │ PostgreSQL (Supabase) │
            │ - Ticket updated      │
            │ - Activity logged     │
            └───────────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │ Response to Client    │
            │ {                     │
            │   id: 123,            │
            │   ticket_number:      │
            │   "TKT-2026-0001",    │
            │   status: "open",     │
            │   category: "access", │
            │   priority: "high"    │
            │ }                     │
            └───────────────────────┘
```

## 📊 Database Schema

### Tables Required:
1. **users** - Employee and IT staff
2. **tickets** - Support tickets  
3. **ticket_activities** - Audit log
4. **sla_policies** - SLA rules by priority
5. **knowledge_base** - FAQs and solutions

## 🔧 Current Implementation Status

### ✅ Working Components:
- n8n Classification Webhook: `http://143.244.136.25:5678/webhook/classify-ticket`
- Backend Health Check: `http://143.244.136.25:8000/health`
- FastAPI Documentation: `http://143.244.136.25:8000/docs`

### ⚠️ Issues Found:
- **500 Internal Server Error** on ticket/user endpoints
- **Root Cause**: Database tables may be missing or SLA policies not initialized
- **Solution**: Run database initialization script

## 🚀 n8n Workflow Details

### Current Nodes (from screenshot):
1. **Webhook** - Receives POST request with ticket data
2. **Prepare Classification Input** - Formats data for AI
3. **Call Gemini AI** - POST to Gemini API for classification
4. **Parse AI Response** - Extracts category, priority, confidence
5. **Send Response** - Returns classification to backend

### Removed Node:
- **Update Backend** - Was removed due to previous errors
- **Current Status**: Backend handles response synchronously instead

## 🔌 API Endpoints

### Ticket Endpoints:
```
POST   /api/v1/tickets/              - Create ticket
GET    /api/v1/tickets/              - List tickets (with filters)
GET    /api/v1/tickets/{id}          - Get ticket details
GET    /api/v1/tickets/number/{num}  - Get by ticket number
PATCH  /api/v1/tickets/{id}          - Update ticket
PATCH  /api/v1/tickets/{id}/status   - Change status
PATCH  /api/v1/tickets/{id}/assign   - Assign to IT staff
POST   /api/v1/tickets/{id}/comments - Add comment
GET    /api/v1/tickets/{id}/activities - Get history
DELETE /api/v1/tickets/{id}          - Cancel ticket
```

### User Endpoints:
```
POST   /api/v1/users/               - Create user
GET    /api/v1/users/               - List users
GET    /api/v1/users/{id}           - Get user
PATCH  /api/v1/users/{id}           - Update user
GET    /api/v1/users/slack/{id}     - Get by Slack ID
```

## 🧪 Testing n8n Integration

### Test 1: Direct n8n Webhook
```bash
curl -X POST http://143.244.136.25:5678/webhook/classify-ticket \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": 123,
    "title": "Cannot login to system",
    "description": "User unable to login, getting invalid credentials error"
  }'
```

**Expected Response:**
```json
{
  "ticket_id": 123,
  "classification": {
    "category": "access",
    "priority": "high",
    "suggested_team": "Identity and Access Management",
    "confidence": "high",
    "reasoning": "Login issue indicates access problem..."
  }
}
```

### Test 2: Backend Ticket Creation (after fix)
```bash
curl -X POST http://143.244.136.25:8000/api/v1/tickets/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cannot login to system",
    "description": "User unable to login, getting invalid credentials error",
    "category": "software",
    "user_id": 1
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "ticket_number": "TKT-2026-0001",
  "title": "Cannot login to system",
  "description": "User unable to login...",
  "category": "access",
  "priority": "high",
  "status": "open",
  "ai_classification": "access_high",
  "ai_confidence": 0.9,
  "user_id": 1,
  "created_at": "2026-02-09T15:30:00Z"
}
```

## 🔧 How to Fix Backend 500 Error

### Step 1: Initialize Database Tables
The backend creates tables on startup, but ensure it ran successfully.

### Step 2: Create Default SLA Policies
SLA policies are required for ticket creation. Create them via API or directly in database:

```sql
INSERT INTO sla_policies (priority, response_time_hours, resolution_time_hours, description) VALUES
('low', 24, 72, 'Low priority - 3 business days'),
('medium', 8, 48, 'Medium priority - 2 business days'),
('high', 4, 24, 'High priority - 24 hours'),
('urgent', 1, 8, 'Urgent priority - 8 hours');
```

### Step 3: Create Test User
```bash
curl -X POST http://143.244.136.25:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@fixora.com",
    "full_name": "Test User",
    "department": "IT",
    "role": "employee"
  }'
```

## 📱 Slack Bot Integration

Once backend is fixed, Slack bot will:
1. Receive command `/ticket` or message
2. Parse user request
3. Call backend API to create ticket
4. Backend auto-classifies via n8n
5. Return ticket number to user
6. User can track via ticket number

## 🎯 Next Steps

1. ✅ **n8n webhook** - Already working!
2. ⚠️ **Fix backend database** - Initialize SLA policies
3. 🔄 **Test ticket creation** - Verify full flow
4. 🤖 **Connect Slack bot** - Integrate with working backend
5. 📊 **Add frontend dashboard** - Admin panel for IT staff

## 📝 Notes

- **n8n Update Backend Node**: Removed because backend handles response synchronously
- **AI Confidence**: Converted from "high/medium/low" to 0.9/0.7/0.5
- **Authentication**: Currently using default user_id=1, implement JWT later
- **SLA Calculation**: Automatic based on priority, requires sla_policies table
