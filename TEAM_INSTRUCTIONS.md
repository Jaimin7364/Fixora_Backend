# Fixora Project - Team Instructions for GitHub Copilot

> **Share this document with your teammates. They can use it with GitHub Copilot in VS Code to understand and build their assigned components.**

---

## 🎯 Project Overview

**Fixora** is an AI-powered IT Support System that automates ticket management through:
- Slack bot for users to create/track tickets
- Gemini AI for automatic ticket classification
- n8n for workflow automation
- FastAPI backend for REST APIs
- Next.js admin dashboard for IT staff

---

## 🏗️ System Architecture

```
Employee (User)
    ↓
Slack Bot (Person 3)
    ↓
FastAPI Backend (Person 1) ← You are here (Backend Repository)
    ↓
n8n Workflow (Person 2) → Gemini AI Classification
    ↓
PostgreSQL Database (Supabase - Already configured)
    ↓
Next.js Dashboard (Person 4)
```

---

## 📊 Database Schema (Already Created)

### Tables:

1. **users** - Employee & IT staff
   - `id`, `email`, `full_name`, `teams_user_id` (Slack user ID)
   - `department`, `role` (employee/admin/it_support/manager)
   - `is_active`, `phone`, `created_at`, `updated_at`

2. **tickets** - Support tickets
   - `id`, `ticket_number` (TKT-2026-0001)
   - `user_id`, `assigned_to_id`
   - `title`, `description`, `category`, `priority`, `status`
   - `ai_classification`, `ai_confidence`
   - `sla_deadline`, `resolved_at`, `closed_at`
   - Categories: hardware, software, network, access, email, printer, account, other
   - Priority: low, medium, high, urgent
   - Status: open, in_progress, waiting_on_user, resolved, closed, cancelled

3. **ticket_activities** - Audit trail
   - `id`, `ticket_id`, `user_id`, `activity_type`, `description`
   - `old_value`, `new_value`, `created_at`

4. **knowledge_base** - FAQs & solutions
   - `id`, `title`, `question`, `answer`, `category`
   - `keywords`, `view_count`, `helpful_count`, `is_active`

5. **attachments** - File uploads
   - `id`, `ticket_id`, `file_name`, `file_path`, `file_type`, `file_size`

6. **sla_policies** - SLA configuration
   - `id`, `priority`, `response_time_hours`, `resolution_time_hours`

---

## 👥 Team Assignments

### **Person 1: Backend APIs (FastAPI)** 🔧
**Repository**: `Fixora_Backend` (this repo)
**Your Tasks**:
- Create Pydantic schemas for validation
- Build service layer with business logic
- Implement REST API endpoints
- Add database session management
- Create API documentation

### **Person 2: n8n Workflows + AI** 🤖
**Repository**: `Fixora_n8n_Workflows` (create new)
**Your Tasks**:
- Design n8n workflow for AI classification
- Integrate Google Gemini API
- Create webhook endpoints
- Build classification logic
- Test and optimize prompts

### **Person 3: Slack Bot** 💬
**Repository**: `Fixora_Slack_Bot` (create new)
**Your Tasks**:
- Create Slack app and get credentials
- Implement event handlers
- Build slash commands
- Create interactive messages
- Integrate with backend APIs

### **Person 4: Next.js Dashboard** 🎨
**Repository**: `Fixora_Dashboard` (create new)
**Your Tasks**:
- Setup Next.js with TypeScript
- Design dashboard UI/UX
- Build ticket management pages
- Create analytics/metrics views
- Integrate with backend APIs

---

## 🚀 Setup Instructions

### **Prerequisites (All Team Members)**
```bash
# Install tools
- Git
- VS Code with GitHub Copilot extension
- Python 3.13+ (Person 1, 3)
- Node.js 18+ (Person 2, 3, 4)
- Docker (Person 2)
```

### **Backend Setup (Person 1)**
```bash
# Clone repository
git clone https://github.com/Jaimin7364/Fixora_Backend.git
cd Fixora_Backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from team)
# DATABASE_URL=postgresql://postgres.XXX...

# Run server
uvicorn app.main:app --reload

# Access API docs
# http://localhost:8000/docs
```

### **n8n Setup (Person 2)**
```bash
# Create new directory
mkdir fixora-n8n-workflows
cd fixora-n8n-workflows

# Access n8n server (already deployed)
# URL: http://143.244.136.25:5678
# Credentials: [Get from team]

# Create workflows in n8n UI
# Export and save to this repo
```

### **Slack Bot Setup (Person 3)**
```bash
# Create new repository
mkdir fixora-slack-bot
cd fixora-slack-bot
git init

# Install Slack Bolt
pip install slack-bolt python-dotenv requests

# Create app at https://api.slack.com/apps
# Get tokens and add to .env
```

### **Dashboard Setup (Person 4)**
```bash
# Create Next.js app
npx create-next-app@latest fixora-dashboard --typescript --tailwind --app
cd fixora-dashboard

# Install dependencies
npm install axios @tanstack/react-query recharts

# Create .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 📋 Person 1: Backend API Development Guide

### **Phase 1: Pydantic Schemas**

**File**: `app/schemas/user.py`
```python
# Create request/response models for User
# - UserBase: Common fields
# - UserCreate: For creating users
# - UserUpdate: For updating users
# - UserResponse: For API responses
# Include validation (email format, phone, etc.)
```

**File**: `app/schemas/ticket.py`
```python
# Create schemas for Ticket
# - TicketCreate: title, description, category
# - TicketUpdate: status, priority, assigned_to
# - TicketResponse: All fields + user info
# - TicketList: Paginated list response
```

**File**: `app/schemas/kb.py`
```python
# Create schemas for Knowledge Base
# - KBCreate, KBUpdate, KBResponse
# - KBSearchRequest, KBSearchResponse
```

### **Phase 2: Service Layer**

**File**: `app/services/ticket_service.py`
```python
# Implement business logic:
# - create_ticket(db, ticket_data, user_id)
# - get_ticket(db, ticket_id)
# - list_tickets(db, filters, pagination)
# - update_ticket(db, ticket_id, update_data)
# - assign_ticket(db, ticket_id, assigned_to_id)
# - add_comment(db, ticket_id, comment)
# - generate_ticket_number() -> "TKT-2026-0001"
```

**File**: `app/services/user_service.py`
```python
# Implement:
# - create_user(db, user_data)
# - get_user_by_email(db, email)
# - get_user_by_slack_id(db, slack_id)
```

### **Phase 3: API Routes**

**File**: `app/api/v1/ticket_routes.py`
```python
# Create endpoints:
# POST   /tickets/                    Create ticket
# GET    /tickets/                    List all tickets
# GET    /tickets/{id}                Get ticket details
# PATCH  /tickets/{id}                Update ticket
# DELETE /tickets/{id}                Delete ticket
# POST   /tickets/{id}/comments       Add comment
# PATCH  /tickets/{id}/status         Change status
# PATCH  /tickets/{id}/assign         Assign ticket
# GET    /tickets/user/{user_id}      Get user's tickets
```

**File**: `app/api/v1/kb_routes.py`
```python
# Create endpoints:
# GET    /kb/                        List KB articles
# GET    /kb/search?q=keyword        Search KB
# POST   /kb/                        Create article (admin)
# GET    /kb/{id}                    Get article
# PATCH  /kb/{id}                    Update article
# POST   /kb/{id}/helpful            Mark helpful
```

### **Dependencies Pattern**
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.session import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Use in routes:
@router.get("/tickets/")
def list_tickets(db: Session = Depends(get_db)):
    # Your logic
```

---

## 📋 Person 2: n8n Workflow Guide

### **Workflow: AI Ticket Classification**

**Trigger**: Webhook (POST from FastAPI)
**Input**:
```json
{
  "ticket_id": 123,
  "title": "Laptop screen flickering",
  "description": "Screen flickering after Windows update"
}
```

**Steps**:
1. **Webhook Node**: Receive ticket data
2. **Function Node**: Prepare prompt for Gemini
3. **HTTP Request Node**: Call Gemini API
4. **Function Node**: Parse AI response
5. **HTTP Request Node**: Send result back to FastAPI

**Gemini Prompt Template**:
```
Analyze this IT support ticket and classify it:

Title: {{$json.title}}
Description: {{$json.description}}

Provide classification in JSON format:
{
  "category": "hardware|software|network|access|email|printer|account|other",
  "priority": "low|medium|high|urgent",
  "suggested_team": "Hardware Team|Software Team|Network Team|Access Team",
  "confidence": "high|medium|low",
  "reasoning": "Brief explanation"
}
```

**Output to Backend**:
```json
{
  "ticket_id": 123,
  "classification": {
    "category": "hardware",
    "priority": "high",
    "suggested_team": "Hardware Team",
    "confidence": "high"
  }
}
```

**Webhook URLs to Create**:
- `http://YOUR_N8N:5678/webhook/classify-ticket`
- `http://YOUR_N8N:5678/webhook/suggest-solution`

---

## 📋 Person 3: Slack Bot Guide

### **Slack App Setup**

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "Fixora IT Support"
4. Select workspace

**OAuth Scopes Required**:
```
Bot Token Scopes:
- app_mentions:read
- chat:write
- commands
- im:history
- im:read
- im:write
- users:read
```

### **Slash Commands to Create**

| Command | Description | Usage |
|---------|-------------|-------|
| `/ticket` | Create new ticket | `/ticket My laptop won't start` |
| `/status` | Check ticket status | `/status TKT-2026-0001` |
| `/mytickets` | List my tickets | `/mytickets` |
| `/kb` | Search knowledge base | `/kb printer setup` |

### **Bot Features**

**1. Create Ticket via Message**
```python
# When user DMs bot or mentions it:
"My printer is not working"
↓
Bot creates ticket via API
↓
Reply: "✅ Ticket TKT-2026-0042 created (Priority: Medium)"
```

**2. Interactive Buttons**
```python
# After creating ticket, show buttons:
[View Details] [Cancel Ticket] [Add More Info]
```

**3. Status Updates**
```python
# Send notification when ticket status changes:
"🔔 Your ticket TKT-2026-0042 has been assigned to John (IT Support)"
```

### **Code Structure**
```python
# app.py
from slack_bolt import App
import requests

app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
BACKEND_API = "http://localhost:8000/api/v1"

@app.command("/ticket")
def create_ticket_command(ack, command, client):
    # Call backend API to create ticket
    # Send response to user

@app.event("app_mention")
def handle_mention(event, say):
    # Extract text
    # Create ticket
    # Reply

@app.action("view_ticket")
def view_ticket_action(ack, body, client):
    # Fetch ticket details
    # Show modal

if __name__ == "__main__":
    app.start(port=3000)
```

---

## 📋 Person 4: Next.js Dashboard Guide

### **Project Structure**
```
fixora-dashboard/
├── app/
│   ├── dashboard/
│   │   ├── page.tsx              # Dashboard home
│   │   ├── tickets/
│   │   │   ├── page.tsx          # Ticket list
│   │   │   └── [id]/page.tsx    # Ticket details
│   │   ├── analytics/page.tsx    # Analytics
│   │   └── kb/page.tsx           # Knowledge base
│   ├── layout.tsx
│   └── page.tsx                  # Landing page
├── components/
│   ├── TicketCard.tsx
│   ├── TicketTable.tsx
│   ├── StatCard.tsx
│   └── Charts/
│       ├── CategoryChart.tsx
│       └── TrendChart.tsx
├── lib/
│   ├── api.ts                    # API client
│   └── types.ts                  # TypeScript types
└── .env.local
```

### **API Integration**

**File**: `lib/api.ts`
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function fetchTickets() {
  const res = await fetch(`${API_URL}/tickets/`);
  return res.json();
}

export async function fetchTicket(id: number) {
  const res = await fetch(`${API_URL}/tickets/${id}`);
  return res.json();
}

export async function createTicket(data: TicketCreate) {
  const res = await fetch(`${API_URL}/tickets/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return res.json();
}
```

### **Dashboard Pages**

**1. Dashboard Home** (`/dashboard`)
- Total tickets
- Open tickets
- Resolved today
- Average resolution time
- Recent activity

**2. Ticket List** (`/dashboard/tickets`)
- Table with filters (status, priority, category)
- Search functionality
- Pagination
- Click to view details

**3. Ticket Details** (`/dashboard/tickets/[id]`)
- Full ticket information
- Activity timeline
- Comments section
- Status change buttons
- Assignment dropdown

**4. Analytics** (`/dashboard/analytics`)
- Tickets by category (pie chart)
- Tickets by status (bar chart)
- Trend over time (line chart)
- Top issues

---

## 🔌 API Contract (For Integration)

### **Backend Endpoints Person 1 Must Provide**

```typescript
// Types for reference
interface Ticket {
  id: number;
  ticket_number: string;
  title: string;
  description: string;
  category: 'hardware' | 'software' | 'network' | 'access' | 'email' | 'printer' | 'account' | 'other';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'open' | 'in_progress' | 'waiting_on_user' | 'resolved' | 'closed' | 'cancelled';
  user_id: number;
  assigned_to_id?: number;
  ai_classification?: string;
  created_at: string;
  updated_at: string;
}

// Endpoints
POST   /api/v1/tickets/              # Create ticket
GET    /api/v1/tickets/              # List tickets (?status=open&priority=high)
GET    /api/v1/tickets/{id}          # Get ticket
PATCH  /api/v1/tickets/{id}          # Update ticket
POST   /api/v1/tickets/{id}/comments # Add comment
PATCH  /api/v1/tickets/{id}/status   # Change status
GET    /api/v1/metrics/dashboard     # Dashboard stats
GET    /api/v1/kb/search?q=keyword   # Search KB
```

---

## 🔗 Integration Points & Sync

### **Week 1 - Setup**
- **Day 1**: All team members clone/create repos
- **Day 2**: Person 1 shares database schema & API specs
- **Day 3**: Person 2 shares n8n webhook URLs
- **Day 4**: Person 3 gets Slack app credentials
- **Day 5**: Team sync - demo progress

### **Week 2 - Development**
- **Person 1**: Complete ticket APIs
- **Person 2**: n8n workflow working
- **Person 3**: Slash commands implemented
- **Person 4**: Basic dashboard pages

### **Week 3 - Integration**
- Connect all components
- End-to-end testing
- Bug fixes

---

## 📝 Environment Variables

### **Person 1 (Backend) - `.env`**
```env
DATABASE_URL=postgresql://postgres.XXX@aws-1-region.pooler.supabase.com:5432/postgres
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-key
N8N_WEBHOOK_URL=http://143.244.136.25:5678/webhook/classify-ticket
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX
```

### **Person 2 (n8n) - In n8n credentials**
```
GEMINI_API_KEY=your-gemini-api-key
BACKEND_API_URL=http://localhost:8000/api/v1
```

### **Person 3 (Slack Bot) - `.env`**
```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
BACKEND_API_URL=http://localhost:8000/api/v1
```

### **Person 4 (Dashboard) - `.env.local`**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 🎯 Daily Workflow with GitHub Copilot

### **For All Team Members**:

1. **Open VS Code** with GitHub Copilot enabled
2. **Open this file** (`TEAM_INSTRUCTIONS.md`)
3. **Keep it in a split view** while coding
4. **Ask Copilot** by selecting relevant sections and using Copilot Chat

### **Example Copilot Prompts**:

**Person 1 (Backend)**:
```
"Based on the ticket schema in TEAM_INSTRUCTIONS.md, create Pydantic schemas for ticket CRUD operations"

"Create a FastAPI endpoint to list tickets with filters for status and priority"

"Implement ticket service with create, read, update, delete operations using SQLAlchemy"
```

**Person 2 (n8n)**:
```
"Design a Gemini API prompt for IT ticket classification based on the categories in TEAM_INSTRUCTIONS.md"

"Create a function to parse Gemini API response and extract category, priority, and confidence"
```

**Person 3 (Slack Bot)**:
```
"Create a Slack slash command handler for /ticket that calls the backend API"

"Build interactive buttons for ticket actions using Slack Block Kit"
```

**Person 4 (Dashboard)**:
```
"Create a Next.js page to display a list of tickets fetched from the API"

"Build a ticket detail page with comments section and status update functionality"

"Create a dashboard component showing ticket statistics using Recharts"
```

---

## 🐛 Common Issues & Solutions

### **Database Connection Issues**
```python
# Use Session Pooler URL, not direct connection
DATABASE_URL=postgresql://postgres.PROJECT:PASSWORD@aws-1-region.pooler.supabase.com:5432/postgres
```

### **CORS Issues (Dashboard ↔ Backend)**
```python
# In backend app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **n8n Webhook Not Accessible**
```bash
# Check firewall
ufw status
# Ensure port 5678 is allowed
```

---

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **n8n Docs**: https://docs.n8n.io
- **Slack API**: https://api.slack.com
- **Next.js Docs**: https://nextjs.org/docs
- **Gemini API**: https://ai.google.dev/docs
- **SQLAlchemy**: https://docs.sqlalchemy.org

---

## 🤝 Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Commit often
git add .
git commit -m "feat: description"

# Push to GitHub
git push origin feature/your-feature-name

# Create Pull Request
# Get code review from team
# Merge to main
```

---

## ✅ Definition of Done

### **Backend (Person 1)**
- [ ] All API endpoints working
- [ ] API documentation generated
- [ ] Database operations tested
- [ ] Error handling implemented

### **n8n (Person 2)**
- [ ] Workflow created and tested
- [ ] Gemini classification accurate
- [ ] Webhooks working
- [ ] Workflow exported to repo

### **Slack Bot (Person 3)**
- [ ] All slash commands working
- [ ] Messages sent successfully
- [ ] Interactive buttons functional
- [ ] Error messages handled

### **Dashboard (Person 4)**
- [ ] All pages responsive
- [ ] API integration complete
- [ ] Charts displaying data
- [ ] User experience smooth

---

## 📞 Contact & Support

**Team Lead**: Jaimin Raval
**GitHub**: Jaimin7364
**Repository**: https://github.com/Jaimin7364/Fixora_Backend

**For Questions**:
- Use team Slack channel
- Create GitHub issues
- Daily standup meetings

---

## 🚀 Let's Build Fixora!

**Remember**: 
- Ask GitHub Copilot for help
- Reference this document
- Commit code frequently
- Test your changes
- Communicate with team

**Good luck! 🎉**
