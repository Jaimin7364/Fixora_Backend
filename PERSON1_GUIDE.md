# 🚀 Person 1 - Backend API Setup & Testing Guide

## ✅ Phase 1: Completed Files

### Pydantic Schemas (Data Validation)
- ✅ `app/schemas/user.py` - User validation models
- ✅ `app/schemas/ticket.py` - Ticket validation models
- ✅ `app/schemas/kb.py` - Knowledge base validation models

### Service Layer (Business Logic)
- ✅ `app/services/user_service.py` - User CRUD operations
- ✅ `app/services/ticket_service.py` - Ticket management with SLA
- ✅ `app/services/kb_service.py` - Knowledge base operations
- ✅ `app/services/slack_service.py` - Slack notifications
- ✅ `app/services/n8n_service.py` - AI classification integration

### API Routes
- ✅ `app/api/v1/ticket_routes.py` - Ticket endpoints
- ✅ `app/api/v1/user_routes.py` - User endpoints
- ✅ `app/api/v1/kb_routes.py` - Knowledge base endpoints
- ✅ `app/api/v1/slack_routes.py` - Slack integration endpoints
- ✅ `app/api/v1/metrics_routes.py` - Analytics & dashboard metrics

### Configuration
- ✅ `app/core/config.py` - Enhanced settings
- ✅ `app/main.py` - FastAPI app with CORS
- ✅ `app/database/session.py` - DB session with dependency injection
- ✅ `app/api/v1/api_router.py` - All routes registered

---

## 🔧 Setup Instructions

### Step 1: Install Dependencies
```bash
cd Fixora_Backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy example environment file
copy .env.example .env

# Edit .env and add your database URL
# Get DATABASE_URL from Supabase project settings
```

### Step 3: Run the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Access API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

---

## 📝 API Testing Guide

### 1. Test User Endpoints

#### Create a User
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@company.com",
    "full_name": "John Doe",
    "department": "Engineering",
    "role": "employee",
    "phone": "+1-555-0123"
  }'
```

#### List Users
```bash
curl "http://localhost:8000/api/v1/users/"
```

### 2. Test Ticket Endpoints

#### Create a Ticket
```bash
curl -X POST "http://localhost:8000/api/v1/tickets/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Laptop screen flickering",
    "description": "My laptop screen has been flickering since this morning after Windows update",
    "category": "hardware",
    "user_id": 1
  }'
```

#### List All Tickets
```bash
curl "http://localhost:8000/api/v1/tickets/"
```

#### Filter Tickets by Status
```bash
curl "http://localhost:8000/api/v1/tickets/?status=open&priority=high"
```

#### Get Ticket Details
```bash
curl "http://localhost:8000/api/v1/tickets/1"
```

#### Update Ticket Status
```bash
curl -X PATCH "http://localhost:8000/api/v1/tickets/1/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }'
```

#### Assign Ticket
```bash
curl -X PATCH "http://localhost:8000/api/v1/tickets/1/assign" \
  -H "Content-Type: application/json" \
  -d '{
    "assigned_to_id": 2
  }'
```

#### Add Comment
```bash
curl -X POST "http://localhost:8000/api/v1/tickets/1/comments" \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "I have looked into this issue and will resolve it soon"
  }'
```

### 3. Test Knowledge Base Endpoints

#### Create KB Article
```bash
curl -X POST "http://localhost:8000/api/v1/kb/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "How to fix printer offline issue",
    "question": "My printer shows as offline, how do I fix it?",
    "answer": "1. Check if printer is powered on\n2. Verify USB/network cable\n3. Restart print spooler service\n4. Set as default printer",
    "category": "printer",
    "keywords": "printer, offline, not printing, connection",
    "is_featured": true
  }'
```

#### Search Knowledge Base
```bash
curl "http://localhost:8000/api/v1/kb/search?q=printer"
```

#### Mark Article as Helpful
```bash
curl -X POST "http://localhost:8000/api/v1/kb/1/helpful?helpful=true"
```

### 4. Test Metrics Endpoints

#### Dashboard Statistics
```bash
curl "http://localhost:8000/api/v1/metrics/dashboard"
```

#### Tickets by Category
```bash
curl "http://localhost:8000/api/v1/metrics/tickets-by-category"
```

#### Tickets by Status
```bash
curl "http://localhost:8000/api/v1/metrics/tickets-by-status"
```

#### SLA Compliance
```bash
curl "http://localhost:8000/api/v1/metrics/sla-compliance"
```

---

## 🧪 Testing with Swagger UI (Recommended)

1. Open http://localhost:8000/docs
2. Try each endpoint interactively
3. See request/response examples
4. No need for curl commands!

### Test Workflow in Swagger:

1. **Create a user** (POST /users/)
2. **Create a ticket** (POST /tickets/)
3. **List tickets** (GET /tickets/)
4. **View ticket details** (GET /tickets/{id})
5. **Add a comment** (POST /tickets/{id}/comments)
6. **Change status** (PATCH /tickets/{id}/status)
7. **Check metrics** (GET /metrics/dashboard)

---

## 📊 Key Features Implemented

### Ticket Service
- ✅ Auto-generate ticket numbers (TKT-2026-0001)
- ✅ Calculate SLA deadlines based on priority
- ✅ Track all changes in activity log
- ✅ Filter & search functionality
- ✅ Pagination support
- ✅ AI classification integration ready

### User Service
- ✅ CRUD operations
- ✅ Slack ID lookup
- ✅ Email validation
- ✅ Phone format validation
- ✅ Role-based filtering

### Knowledge Base Service
- ✅ Full-text search
- ✅ View count tracking
- ✅ Helpful/not helpful voting
- ✅ Featured articles
- ✅ Category filtering

### Metrics Service
- ✅ Dashboard statistics
- ✅ Ticket trends
- ✅ Category/Status/Priority breakdowns
- ✅ SLA compliance tracking
- ✅ Agent performance metrics
- ✅ Resolution time analytics

### Slack Integration
- ✅ Webhook endpoints for events
- ✅ Slash command handlers (/ticket, /status, /mytickets)
- ✅ Interactive button support
- ✅ Notification sending (ready)

### n8n Integration
- ✅ Send tickets for AI classification
- ✅ Receive classification results
- ✅ Parse and apply AI suggestions
- ✅ Confidence scoring

---

## 🔗 Integration Points

### For Person 2 (n8n):
- Send POST to: `/api/v1/slack/webhook/classification`
- Expected format documented in `slack_routes.py`

### For Person 3 (Slack Bot):
- Use endpoints in `/api/v1/tickets/` and `/api/v1/users/`
- Webhook endpoint: `/api/v1/slack/events`
- Commands endpoint: `/api/v1/slack/commands`

### For Person 4 (Dashboard):
- All endpoints available at `/api/v1/`
- Full API documentation at `/docs`
- CORS already configured for `localhost:3000`

---

## ⚠️ Important Notes

### TODO Items (For Later):
1. Add JWT authentication (currently using placeholder user_id=1)
2. Implement file upload for attachments
3. Add email notifications
4. Add rate limiting
5. Add request validation middleware
6. Add logging to files
7. Add database migrations (Alembic)

### Current Limitations:
- No authentication (uses dummy user_id)
- No file attachments yet
- No email sending
- Slack verification disabled if secrets not configured

---

## 🎯 Next Steps

1. **Test all endpoints** in Swagger UI
2. **Create sample data** (users, tickets, KB articles)
3. **Test with Person 3** (Slack integration)
4. **Test with Person 4** (Dashboard integration)
5. **Setup n8n webhook** with Person 2

---

## 🐛 Troubleshooting

### Database Connection Error
```bash
# Check DATABASE_URL in .env
# Ensure Supabase project is running
# Use Session Pooler URL, not direct connection
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### CORS Errors
```bash
# Check main.py - allowed origins should include your frontend URL
```

---

## 📚 API Documentation

Full interactive documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## ✅ Checklist

- [x] All Pydantic schemas created
- [x] All service layers implemented
- [x] All API routes created
- [x] Database session management configured
- [x] CORS configured
- [x] Error handling implemented
- [x] API documentation auto-generated
- [x] Integration points defined
- [ ] Test with real database
- [ ] Test with Slack Bot (Person 3)
- [ ] Test with Dashboard (Person 4)
- [ ] Test with n8n (Person 2)

---

**Great job! All Phase 1-3 code is complete and ready to test! 🎉**
