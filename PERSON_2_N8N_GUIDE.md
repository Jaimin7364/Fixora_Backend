# Person 2: n8n Workflows + AI Integration - Complete Guide

**Your Role**: Build AI-powered ticket classification using n8n and Gemini API

---

## 🎯 Your Responsibilities

1. ✅ Design n8n workflows for AI classification
2. ✅ Integrate Google Gemini API
3. ✅ Create webhook endpoints for backend
4. ✅ Build intelligent classification logic
5. ✅ Test and optimize AI prompts
6. ✅ Export workflows for team

---

## 🚀 Quick Start

### **Step 1: Access n8n Server**

You already have n8n running at:
```
URL: http://143.244.136.25:5678
```

Login credentials: [Use what you set up during installation]

---

### **Step 2: Get Gemini API Key**

1. Go to https://makersuite.google.com/app/apikey
2. Click **"Create API Key"**
3. Select project or create new one
4. Copy the API key: `AIzaSy...`
5. Save it securely

---

### **Step 3: Create Local Workspace**

```bash
# Create directory for workflow files
mkdir ~/fixora-n8n-workflows
cd ~/fixora-n8n-workflows

# Initialize git
git init

# Create README
cat > README.md << 'EOF'
# Fixora n8n Workflows

This repository contains n8n workflow definitions for the Fixora IT Support System.

## Workflows

1. **Ticket Classification** - AI-powered ticket categorization
2. **Solution Suggestion** - Knowledge base search and AI suggestions
3. **Auto-Assignment** - Intelligent ticket routing

## Setup

Import these workflows into your n8n instance.
EOF

# Create GitHub repository
gh repo create Fixora_n8n_Workflows --public --source=. --remote=origin --push
```

---

## 📋 Workflow 1: AI Ticket Classification

### **Overview**

**Purpose**: Automatically classify support tickets using Gemini AI
**Trigger**: Webhook from FastAPI backend
**Output**: Classification data sent back to backend

### **Workflow Diagram**

```
[Webhook Trigger]
      ↓
[Parse Input Data]
      ↓
[Build Gemini Prompt]
      ↓
[Call Gemini API]
      ↓
[Parse AI Response]
      ↓
[Validate Classification]
      ↓
[Send to Backend]
      ↓
[Return Response]
```

---

## 🔧 Building the Workflow

### **Step 1: Open n8n and Create New Workflow**

1. Login to http://143.244.136.25:5678
2. Click **"Add Workflow"**
3. Name: `Ticket Classification`
4. Click **"Save"**

---

### **Step 2: Add Webhook Trigger**

1. Click **"+"** to add node
2. Search: **"Webhook"**
3. Select **"Webhook"**
4. Configure:
   - **HTTP Method**: POST
   - **Path**: `classify-ticket`
   - **Response Mode**: When Last Node Finishes
   - **Response Data**: First Entry JSON

5. Click **"Execute Node"** to get webhook URL
6. **Copy the webhook URL**: `http://143.244.136.25:5678/webhook/classify-ticket`
7. **Save this URL** - backend will use it

---

### **Step 3: Add Function Node - Prepare Input**

1. Add **Function** node after Webhook
2. Name: `Prepare Classification Input`
3. JavaScript Code:

```javascript
// Get webhook data from body
const ticketData = $input.all()[0].json.body;

// Extract fields
const ticketId = ticketData.ticket_id;
const title = ticketData.title || '';
const description = ticketData.description || '';

// Combine text for AI
const fullText = `Title: ${title}\n\nDescription: ${description}`;

// Build complete Gemini API request body
const geminiRequestBody = {
  contents: [{
    parts: [{
      text: `You are an IT support ticket classifier. Analyze the following ticket and provide classification.

Ticket: ${fullText}

Provide your response in this exact JSON format:
{
  "category": "one of: hardware, software, network, access, email, printer, account, other",
  "priority": "one of: low, medium, high, urgent",
  "suggested_team": "team name",
  "confidence": "one of: high, medium, low",
  "reasoning": "brief explanation"
}

Respond ONLY with valid JSON, no other text.`
    }]
  }]
};

return {
  ticket_id: ticketId,
  full_text: fullText,
  title: title,
  description: description,
  gemini_body: geminiRequestBody
};
```

4. Click **"Test step"**

---

### **Step 4: Add HTTP Request Node - Call Gemini API**

1. Add **HTTP Request** node
2. Name: `Call Gemini AI`
3. Configure:

**Authentication**: None (using API key in URL)

**Request Method**: POST

**URL**: 
```
https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=YOUR_GEMINI_API_KEY
```

**Body Content Type**: JSON

**Body (fx enabled, expression)**:
```
={{ $('Prepare Classification Input').item.json.gemini_body }}
```

**Options**:
- **Response Format**: JSON
- **Timeout**: 30000 (30 seconds)

5. Click **"Execute Node"** to test

---

### **Step 5: Add Function Node - Parse Gemini Response**

1. Add **Function** node
2. Name: `Parse AI Response`
3. JavaScript Code:

```javascript
// Get Gemini response
const geminiResponse = $input.all()[0].json;
const ticketId = $('Prepare Classification Input').item.json.ticket_id;

// Extract AI text from Gemini response
let aiText = '';
try {
  if (geminiResponse.candidates && geminiResponse.candidates[0]) {
    aiText = geminiResponse.candidates[0].content.parts[0].text;
  }
} catch (error) {
  throw new Error('Failed to parse Gemini response: ' + error.message);
}

// Clean up response - remove markdown code blocks if present
aiText = aiText.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();

// Parse JSON
let classification;
try {
  classification = JSON.parse(aiText);
} catch (error) {
  throw new Error('AI response is not valid JSON: ' + aiText);
}

// Validate required fields
const validCategories = ['hardware', 'software', 'network', 'access', 'email', 'printer', 'account', 'other'];
const validPriorities = ['low', 'medium', 'high', 'urgent'];
const validConfidence = ['high', 'medium', 'low'];

if (!validCategories.includes(classification.category)) {
  classification.category = 'other';
}

if (!validPriorities.includes(classification.priority)) {
  classification.priority = 'medium';
}

if (!validConfidence.includes(classification.confidence)) {
  classification.confidence = 'medium';
}

// Return formatted result
return {
  ticket_id: ticketId,
  classification: {
    category: classification.category,
    priority: classification.priority,
    suggested_team: classification.suggested_team || 'General Support',
    confidence: classification.confidence,
    reasoning: classification.reasoning || 'Automated classification'
  },
  raw_ai_response: aiText
};
```

4. Click **"Execute Node"**

---

### **Step 6: Add HTTP Request Node - Send to Backend**

1. Add **HTTP Request** node
2. Name: `Update Backend`
3. Configure:

**Method**: PATCH

**URL**: 
```
http://YOUR_BACKEND_IP:8000/api/v1/tickets/{{ $json.ticket_id }}/classify
```

**Body Content Type**: JSON

**Body**:
```json
{
  "ai_classification": "{{ $json.classification.category }}",
  "ai_confidence": "{{ $json.classification.confidence }}",
  "priority": "{{ $json.classification.priority }}",
  "suggested_team": "{{ $json.classification.suggested_team }}"
}
```

**Note**: For now, this will fail since backend endpoint doesn't exist yet. We'll test after Person 1 creates it.

---

### **Step 7: Add Respond to Webhook Node**

1. Add **Respond to Webhook** node
2. Name: `Send Response`
3. Configure:

**Response Body**:
```json
{
  "success": true,
  "ticket_id": "={{ $('Parse AI Response').item.json.ticket_id }}",
  "classification": "={{ $('Parse AI Response').item.json.classification }}"
}
```

---

### **Step 8: Save and Test Workflow**

1. Click **"Save"** (top right)
2. Click **"Execute Workflow"** to activate webhook
3. Keep workflow tab open (webhook must be listening)

---

## 🧪 Testing the Workflow

### **Test with curl**

Open terminal and run:

```bash
curl -X POST http://143.244.136.25:5678/webhook/classify-ticket \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": 1,
    "title": "Laptop screen flickering",
    "description": "My laptop screen has been flickering since the latest Windows update. It happens randomly throughout the day."
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "ticket_id": 1,
  "classification": {
    "category": "hardware",
    "priority": "high",
    "suggested_team": "Hardware Support Team",
    "confidence": "high",
    "reasoning": "Screen flickering after update indicates potential hardware or driver issue"
  }
}
```

---

### **Test Different Scenarios**

**Test 1: Software Issue**
```bash
curl -X POST http://143.244.136.25:5678/webhook/classify-ticket \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": 2,
    "title": "Cannot install Microsoft Office",
    "description": "Getting error code 0x80070005 when trying to install Office 365"
  }'
```

**Test 2: Network Issue**
```bash
curl -X POST http://143.244.136.25:5678/webhook/classify-ticket \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": 3,
    "title": "Internet not working",
    "description": "WiFi connected but no internet access on my work laptop"
  }'
```

**Test 3: Access/Password Issue**
```bash
curl -X POST http://143.244.136.25:5678/webhook/classify-ticket \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": 4,
    "title": "Forgot password",
    "description": "I forgot my domain password and cannot login to my computer"
  }'
```

---

## 📊 Workflow 2: Solution Suggestion (Bonus)

### **Overview**

**Purpose**: Suggest solutions from knowledge base or AI
**Trigger**: Webhook from backend
**Output**: Suggested solutions

### **Steps**

1. Create new workflow: `Solution Suggestion`
2. Add Webhook trigger: `/webhook/suggest-solution`
3. Add HTTP Request to search knowledge base
4. If no KB match, call Gemini for general solution
5. Return formatted response

**Input**:
```json
{
  "ticket_id": 123,
  "category": "software",
  "description": "Cannot install Office"
}
```

**Gemini Prompt**:
```
You are an IT support expert. Provide step-by-step solution for this issue:

Category: {{ $json.category }}
Issue: {{ $json.description }}

Provide solution in this format:
{
  "solution_steps": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ],
  "estimated_time": "5-10 minutes",
  "difficulty": "easy|medium|hard",
  "requires_admin": true|false
}

Respond with valid JSON only.
```

---

## 📤 Export Workflows

### **Export for Team**

1. Go to workflow
2. Click **"..."** (three dots) → **Download**
3. Save as: `ticket-classification.json`
4. Commit to your repo:

```bash
cd ~/fixora-n8n-workflows
mv ~/Downloads/ticket-classification.json ./workflows/
git add workflows/ticket-classification.json
git commit -m "feat: Add ticket classification workflow"
git push
```

---

## 🔑 Share Credentials with Team

Create `.env.example` in your repo:

```bash
cat > .env.example << 'EOF'
# n8n Server
N8N_URL=http://143.244.136.25:5678
N8N_USERNAME=admin
N8N_PASSWORD=[ask team]

# Webhook URLs
WEBHOOK_CLASSIFY_TICKET=http://143.244.136.25:5678/webhook/classify-ticket
WEBHOOK_SUGGEST_SOLUTION=http://143.244.136.25:5678/webhook/suggest-solution

# Gemini API
GEMINI_API_KEY=[get from Google AI Studio]

# Backend API
BACKEND_API_URL=http://localhost:8000/api/v1
EOF

git add .env.example
git commit -m "docs: Add environment variables template"
git push
```

---

## 📝 Document Your Workflows

Create `WORKFLOWS.md`:

```markdown
# n8n Workflows Documentation

## 1. Ticket Classification

**Webhook URL**: http://143.244.136.25:5678/webhook/classify-ticket

**Input**:
\`\`\`json
{
  "ticket_id": 123,
  "title": "Issue title",
  "description": "Issue description"
}
\`\`\`

**Output**:
\`\`\`json
{
  "success": true,
  "ticket_id": 123,
  "classification": {
    "category": "hardware",
    "priority": "high",
    "suggested_team": "Hardware Team",
    "confidence": "high",
    "reasoning": "Explanation"
  }
}
\`\`\`

**Categories**: hardware, software, network, access, email, printer, account, other
**Priorities**: low, medium, high, urgent
**Confidence**: high, medium, low

## 2. Solution Suggestion

Coming soon...
```

---

## 🎯 Integration with Backend (Person 1)

### **What Person 1 Needs from You**

1. **Webhook URLs**:
   ```
   CLASSIFY_TICKET_WEBHOOK=http://143.244.136.25:5678/webhook/classify-ticket
   SUGGEST_SOLUTION_WEBHOOK=http://143.244.136.25:5678/webhook/suggest-solution
   ```

2. **API Contract** - They need to know:
   - What to send (input format)
   - What they'll receive (output format)
   - Error responses

3. **Testing Access** - Share n8n credentials for debugging

### **How Person 1 Will Call Your Workflow**

In their `app/services/n8n_service.py`:

```python
import httpx

N8N_CLASSIFY_URL = "http://143.244.136.25:5678/webhook/classify-ticket"

async def classify_ticket(ticket_id: int, title: str, description: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            N8N_CLASSIFY_URL,
            json={
                "ticket_id": ticket_id,
                "title": title,
                "description": description
            },
            timeout=30.0
        )
        return response.json()
```

---

## 🔍 Optimization Tips

### **Improve AI Accuracy**

1. **Add Examples to Prompt**:
```
Examples:
- "Printer not working" → category: printer, priority: medium
- "Cannot access SharePoint" → category: access, priority: high
- "Laptop won't turn on" → category: hardware, priority: urgent
```

2. **Use Temperature Parameter**:
```json
{
  "contents": [...],
  "generationConfig": {
    "temperature": 0.2,  // Lower = more consistent
    "topK": 40,
    "topP": 0.95
  }
}
```

3. **Add Context About Company**:
```
Our company uses:
- Windows 10/11 for all laptops
- Office 365 for productivity
- Cisco VPN for remote access
- ServiceNow for internal tools
```

---

## ⚡ Performance Monitoring

### **Add Execution Tracking**

Add a Function node at the end:

```javascript
const startTime = $('Webhook').item.json.__timestamp;
const endTime = Date.now();
const duration = endTime - startTime;

// Log metrics
console.log('Classification completed:', {
  ticket_id: $json.ticket_id,
  duration_ms: duration,
  category: $json.classification.category,
  confidence: $json.classification.confidence
});

return $input.all();
```

---

## 🚨 Error Handling

### **Add Error Catch Node**

1. Select all nodes
2. Click **Settings** → **Error Workflow**
3. Create error handling workflow:

```
[On Error]
    ↓
[Log Error]
    ↓
[Send Notification]
    ↓
[Return Default Classification]
```

---

## ✅ Your Deliverables

- [x] Working ticket classification workflow
- [x] Webhook URLs documented
- [x] Gemini API integrated
- [x] Workflows exported to Git
- [x] API documentation created
- [x] Test cases documented
- [ ] Solution suggestion workflow (optional)

---

## 📞 Communication with Team

### **Share with Person 1 (Backend)**:
```
Hey! n8n classification is ready:

🔗 Webhook: http://143.244.136.25:5678/webhook/classify-ticket

📥 Input format:
{
  "ticket_id": 123,
  "title": "string",
  "description": "string"
}

📤 Output format:
{
  "classification": {
    "category": "hardware|software|...",
    "priority": "low|medium|high|urgent",
    "confidence": "high|medium|low"
  }
}

⏱️ Response time: ~2-5 seconds
```

---

## 🎓 Learning Resources

- **n8n Docs**: https://docs.n8n.io
- **Gemini API**: https://ai.google.dev/docs
- **Workflow Examples**: https://n8n.io/workflows

---

## 🐛 Troubleshooting

**Issue**: Gemini returns invalid JSON
**Solution**: Add JSON cleanup in parse function

**Issue**: Webhook timeout
**Solution**: Increase timeout in HTTP Request node

**Issue**: n8n server not accessible
**Solution**: Check firewall, ensure port 5678 is open

---

**You're all set! Start building your workflows! 🚀**
