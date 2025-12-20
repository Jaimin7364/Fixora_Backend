# Fixora - AI-Powered IT Support System

**Backend API for AI-driven IT Helpdesk integrated with Slack**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-blue.svg)](https://www.postgresql.org/)

---

## 📋 Project Overview

Fixora is an **AI-driven IT Helpdesk system** that enables employees to:
- Raise support tickets via Slack bot
- Get AI-powered troubleshooting advice
- Track ticket status in real-time
- Access knowledge base for common issues
- Auto-route and classify tickets using Gemini AI

This system replaces manual email-based ticket creation with an intelligent, automated workflow.

---

## 🏗️ Architecture

```
User (Employee)
    ↓
Slack Bot
    ↓
FastAPI Backend (Python)
    ↓
n8n Workflow Engine → Gemini AI (Classification)
    ↓
PostgreSQL Database (Supabase)
    ↓
Next.js Admin Dashboard
```

---

## 🚀 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.13)
- **Database**: PostgreSQL (Supabase with Session Pooler)
- **ORM**: SQLAlchemy
- **Authentication**: JWT / OAuth2 (planned)
- **API Docs**: Auto-generated with Swagger/OpenAPI

### AI & Automation
- **AI Provider**: Google Gemini API
- **Workflow Engine**: n8n (self-hosted)
- **Classification**: Automatic ticket categorization & priority assignment

### Frontend
- **Admin Dashboard**: Next.js (separate repository)
- **User Interface**: Slack Bot

### Infrastructure
- **Database Hosting**: Supabase
- **Deployment**: Azure (planned)

---

## 📊 Database Schema

### Tables

#### 1. **users**
Employee and IT staff management
- `id`, `email`, `full_name`, `teams_user_id` (Slack user ID)
- `department`, `role` (employee/admin/it_support/manager)
- `is_active`, `phone`, `created_at`, `updated_at`

#### 2. **tickets**
Core ticketing system
- `id`, `ticket_number` (TKT-YYYY-XXXX)
- `user_id`, `assigned_to_id`
- `title`, `description`, `category`, `priority`, `status`
- `ai_classification`, `ai_confidence`
- `sla_deadline`, `resolved_at`, `closed_at`
- `created_at`, `updated_at`

**Status**: `open`, `in_progress`, `waiting_on_user`, `resolved`, `closed`, `cancelled`

**Priority**: `low`, `medium`, `high`, `urgent`

**Category**: `hardware`, `software`, `network`, `access`, `email`, `printer`, `account`, `other`

#### 3. **ticket_activities**
Audit trail and ticket history
- `id`, `ticket_id`, `user_id`
- `activity_type` (created/updated/comment/status_changed/assigned)
- `description`, `old_value`, `new_value`
- `created_at`

#### 4. **knowledge_base**
FAQs and troubleshooting articles
- `id`, `title`, `question`, `answer`, `category`
- `keywords`, `view_count`, `helpful_count`, `not_helpful_count`
- `is_active`, `is_featured`
- `created_at`, `updated_at`

#### 5. **attachments**
File uploads for tickets
- `id`, `ticket_id`, `file_name`, `file_path`, `file_type`, `file_size`
- `uploaded_by`, `uploaded_at`

#### 6. **sla_policies**
SLA configuration by priority
- `id`, `priority`, `response_time_hours`, `resolution_time_hours`
- `description`

---

## 🔧 Setup Instructions

### Prerequisites
- Python 3.13+
- PostgreSQL (Supabase account)
- Git

### 1. Clone Repository
```bash
git clone https://github.com/Jaimin7364/Fixora_Backend.git
cd Fixora_Backend
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres.YOUR_PROJECT_ID:YOUR_PASSWORD@aws-1-region.pooler.supabase.com:5432/postgres

# API Configuration
API_V1_PREFIX=/api/v1
PROJECT_NAME=Fixora

# Security (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_SIGNING_SECRET=your-signing-secret

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# n8n Integration
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/classify
N8N_API_KEY=your-n8n-api-key
```

### 5. Database Migration
Tables are auto-created on startup via SQLAlchemy:
```bash
uvicorn app.main:app --reload
```

### 6. Access API Documentation
Once running, visit:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api_router.py          # Main API router
│   │       ├── ticket_routes.py       # Ticket CRUD endpoints
│   │       ├── kb_routes.py           # Knowledge base endpoints
│   │       ├── slack_routes.py        # Slack bot webhooks
│   │       └── metrics_routes.py      # Analytics & dashboard
│   ├── core/
│   │   ├── config.py                  # App configuration
│   │   └── security.py                # Auth & security
│   ├── database/
│   │   ├── base.py                    # SQLAlchemy base
│   │   └── session.py                 # DB session management
│   ├── models/
│   │   ├── user.py                    # User model
│   │   ├── ticket.py                  # Ticket model
│   │   ├── ticket_activity.py         # Activity log model
│   │   ├── knowledge_base.py          # KB model
│   │   ├── attachment.py              # Attachment model
│   │   └── sla_policy.py              # SLA config model
│   ├── schemas/
│   │   ├── user.py                    # User Pydantic schemas
│   │   ├── ticket.py                  # Ticket Pydantic schemas
│   │   └── kb.py                      # KB Pydantic schemas
│   ├── services/
│   │   ├── ticket_service.py          # Ticket business logic
│   │   ├── slack_service.py           # Slack integration
│   │   └── n8n_service.py             # n8n workflow calls
│   ├── utils/
│   │   ├── helpers.py                 # Utility functions
│   │   └── logger.py                  # Logging config
│   └── main.py                        # FastAPI app entry point
├── .env                               # Environment variables (not in repo)
├── .gitignore                         # Git ignore rules
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

---

## 🔌 API Endpoints (Planned)

### Tickets
- `POST /api/v1/tickets/` - Create new ticket
- `GET /api/v1/tickets/` - List all tickets
- `GET /api/v1/tickets/{id}` - Get ticket details
- `PATCH /api/v1/tickets/{id}` - Update ticket
- `DELETE /api/v1/tickets/{id}` - Delete ticket
- `POST /api/v1/tickets/{id}/comment` - Add comment
- `PATCH /api/v1/tickets/{id}/status` - Change status
- `PATCH /api/v1/tickets/{id}/assign` - Assign ticket

### Knowledge Base
- `GET /api/v1/kb/` - List KB articles
- `GET /api/v1/kb/search` - Search knowledge base
- `POST /api/v1/kb/` - Create KB article (admin)
- `GET /api/v1/kb/{id}` - Get article details

### Slack Integration
- `POST /api/v1/slack/events` - Slack event webhook
- `POST /api/v1/slack/commands` - Slack slash commands
- `POST /api/v1/slack/interactions` - Button/menu interactions

### Metrics & Analytics
- `GET /api/v1/metrics/dashboard` - Dashboard stats
- `GET /api/v1/metrics/tickets/by-category` - Tickets by category
- `GET /api/v1/metrics/tickets/by-status` - Tickets by status
- `GET /api/v1/metrics/resolution-time` - Average resolution time

### Users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/me` - Get current user
- `GET /api/v1/users/` - List users (admin)

---

## 🎯 Key Features

### ✅ Implemented
- [x] Database models and schema
- [x] SQLAlchemy ORM setup
- [x] FastAPI project structure
- [x] PostgreSQL connection (Supabase)
- [x] Environment configuration

### 🚧 In Progress
- [ ] Pydantic schemas (request/response validation)
- [ ] Ticket CRUD APIs
- [ ] Service layer business logic
- [ ] Knowledge base search

### 📋 Planned
- [ ] Slack bot integration
- [ ] n8n workflow automation
- [ ] Gemini AI classification
- [ ] JWT authentication
- [ ] File attachment handling
- [ ] SLA tracking & notifications
- [ ] Admin dashboard APIs
- [ ] Email notifications
- [ ] Multi-language support
- [ ] Advanced analytics

---

## 🔄 Workflow Example

**User creates ticket via Slack:**

1. User sends message in Slack: *"Laptop screen flickering after update"*
2. Slack bot forwards to FastAPI backend
3. Backend calls n8n webhook with ticket text
4. n8n uses Gemini AI to classify:
   - Category: `hardware`
   - Priority: `high`
   - Suggested assignment: Hardware team
5. Ticket created in database with AI metadata
6. Slack bot replies: *"Ticket #TKT-2025-0042 created. Priority: High. Hardware team notified."*
7. Admin dashboard shows new ticket
8. Updates synced back to Slack thread

---

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest

# Check code coverage
pytest --cov=app tests/

# Run linting
flake8 app/

# Format code
black app/
```

---

## 📝 Development Workflow

### Making Changes
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
uvicorn app.main:app --reload

# Commit changes
git add .
git commit -m "Add: your feature description"

# Push to GitHub
git push origin feature/your-feature-name
```

### Database Changes
When modifying models:
1. Update model file in `app/models/`
2. Restart server (auto-creates tables)
3. For production, use Alembic migrations (planned)

---

## 🔐 Security Considerations

- [ ] API key authentication for external services
- [ ] Rate limiting on endpoints
- [ ] Input validation with Pydantic
- [ ] SQL injection prevention (SQLAlchemy ORM)
- [ ] CORS configuration
- [ ] Secrets management (environment variables)
- [ ] JWT token expiration

---

## 📦 Dependencies

Key packages in `requirements.txt`:
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `sqlalchemy` - ORM
- `psycopg2-binary` - PostgreSQL driver
- `pydantic-settings` - Config management
- `python-dotenv` - Environment variables
- `httpx` - Async HTTP client (for n8n/Gemini calls)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

---

## 📞 Support

For issues or questions:
- GitHub Issues: https://github.com/Jaimin7364/Fixora_Backend/issues
- Project Owner: Jaimin Raval

---

## 📄 License

[Specify your license here]

---

## 🗓️ Project Timeline

**Phase 1**: Backend APIs (3 weeks)
**Phase 2**: Slack Bot Integration (2 weeks)
**Phase 3**: n8n + Gemini AI Automation (2 weeks)
**Phase 4**: Admin Dashboard (2 weeks)
**Phase 5**: Testing & QA (2 weeks)

**Total Estimated Time**: ~3 months

---

## 🔗 Related Repositories

- **Frontend Dashboard**: [Coming Soon]
- **n8n Workflows**: [Coming Soon]

---

**Built with ❤️ for efficient IT support automation**
