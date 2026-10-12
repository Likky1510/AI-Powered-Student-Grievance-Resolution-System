# AI-Powered Student Grievance Resolution System - Quick Start Guide

## System Overview

This is a multi-agent grievance management platform with:
- **Classification Agent**: Auto-classifies student complaints
- **Priority Agent**: Assigns priority levels (low, medium, high, urgent)
- **Routing Agent**: Routes to correct department
- **Escalation Agent**: Detects SLA breaches
- **Analytics Agent**: Generates process insights
- **Notification System**: Emails to students, staff, and admins

---

## Running the System

### Prerequisites
- Python 3.10+
- Node.js 18+
- SQLite (included)

### Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend runs at: `http://127.0.0.1:8000`
API Docs: `http://127.0.0.1:8000/docs`

### Start Frontend
```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

Frontend runs at: `http://localhost:5173`

### Seed Demo Data
```bash
cd backend
python -m app.db.seed
```

---

## Demo Accounts

| Role    | Email                      | Password   |
|---------|----------------------------|------------|
| Admin   | admin@college.edu          | admin123   |
| Staff   | fees.staff@college.edu     | staff123   |
| Staff   | hostel.staff@college.edu   | staff123   |
| Student | student@college.edu        | student123 |

---

## Feature Walkthrough

### 1. Student Submits Grievance
- Login as student at `http://localhost:5173/login`
- Click "File a Complaint"
- Type complaint (e.g., "Library WiFi is slow")
- Click "Submit complaint"

**What happens behind the scenes:**
- Classification Agent auto-classifies as "infrastructure"
- Priority Agent assigns priority based on keywords
- Routing Agent sends to "Facilities & Infrastructure" department
- Student receives confirmation email
- Department staff/admins receive notification email
- Grievance saved as `ASSIGNED` status

### 2. Staff Reviews Department Queue
- Login as staff at `http://localhost:5173/login`
- Go to "Department Queue"
- See all grievances assigned to their department
- Sorted by priority (urgent → low) and creation date

### 3. Staff Updates Grievance Status
- Click dropdown next to grievance
- Change status: submitted → in_progress → resolved → closed
- Add optional note
- Student automatically receives status update email

**Status Flow:**
- `submitted` → `categorized` → `assigned` → `in_progress` → `escalated` (if SLA breach) → `resolved` → `closed`

### 4. Admin Views Analytics
- Login as admin at `http://localhost:5173/login`
- Go to "Analytics"
- See:
  - Total, resolved, pending, escalated counts
  - Department-level metrics (resolution time, escalation rate, SLA breaches)
  - Category breakdown
  - AI-generated insights (mock)

### 5. Escalation Monitoring
- Admin can click "Run escalation check" manually
- Automatically runs every 30 minutes in background
- Marks grievances as `escalated` if SLA exceeded
- Sends WhatsApp alert to admin (if Twilio configured)

### 6. View My Cases (Student)
- Login as student
- Go to "My Cases"
- See all submitted grievances
- Click "View timeline" to see status history
- Can submit feedback when grievance is resolved

---

## API Endpoints

### Auth
- `POST /auth/login` - Login with email/password
- `POST /auth/register` - Register new student account

### Grievances
- `POST /grievances` - Submit new grievance
- `GET /grievances/me` - List my grievances
- `GET /grievances/department` - Staff/admin queue
- `GET /grievances/{id}` - Get grievance details
- `GET /grievances/{id}/history` - View status changes
- `PATCH /grievances/{id}/status` - Update status
- `POST /grievances/{id}/feedback` - Submit feedback (after resolved)

### Departments
- `GET /departments` - List all departments
- `POST /departments` - Create new department (admin only)

### Analytics
- `GET /analytics/summary` - Get dashboard metrics (admin only)
- `POST /analytics/run-escalation-check` - Trigger escalation check (admin only)

---

## Testing the System

### Via Swagger UI
1. Open `http://127.0.0.1:8000/docs`
2. Click on endpoint (e.g., `POST /auth/login`)
3. Click "Try it out"
4. Enter values
5. Click "Execute"

### Via Frontend
1. Register new account at `http://localhost:5173/register`
2. Submit grievance as student
3. Login as staff to see queue
4. Update grievance status
5. Login as admin to view analytics

### Via Command Line
```bash
# Login
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student@college.edu&password=student123"

# Submit grievance
curl -X POST http://127.0.0.1:8000/grievances \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"raw_text":"My complaint here"}'
```

---

## Configuring Real Notifications

### SendGrid (Email)
1. Get API key from https://sendgrid.com
2. Update `backend/.env`:
   ```
   SENDGRID_API_KEY=SG.your_key_here
   SENDGRID_FROM_EMAIL=your-email@gmail.com
   ```
3. Restart backend

### Twilio (WhatsApp)
1. Get credentials from https://twilio.com
2. Update `backend/.env`:
   ```
   TWILIO_ACCOUNT_SID=your_sid
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_WHATSAPP_FROM=whatsapp:+your_number
   ADMIN_WHATSAPP_TO=whatsapp:+recipient_number
   ```
3. Restart backend

In mock mode (default), all emails/SMS are logged to console.

---

## Database

- **Default**: SQLite at `backend/grievance.db`
- **Can switch to**: PostgreSQL by updating `DATABASE_URL` in `.env`

### Schema
- `users` - Student, staff, admin accounts
- `departments` - Academic, fees, hostel, etc.
- `grievances` - Main complaint records
- `status_history` - Audit trail of all status changes
- `escalations` - SLA breach records
- `feedback` - Student satisfaction ratings

---

## Project Structure

```
grievance-system/
├── backend/
│   ├── app/
│   │   ├── agents/           # AI agents (classification, routing, escalation, analytics)
│   │   ├── core/             # Config, security, scheduler
│   │   ├── db/               # Database models and seed
│   │   ├── models/           # SQLAlchemy + Pydantic schemas
│   │   ├── routers/          # API endpoints
│   │   └── main.py           # FastAPI app
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Configuration
├── frontend/
│   ├── src/
│   │   ├── api/              # Axios client + auth context
│   │   ├── components/       # Shared UI components
│   │   ├── pages/            # Route pages (Login, Register, Submit, etc.)
│   │   └── App.jsx           # Main routing
│   ├── package.json          # Node dependencies
│   └── vite.config.js        # Vite config
└── docker-compose.yml        # Docker setup
```

---

## Troubleshooting

### Backend won't start
- Ensure Python 3.10+ and all requirements installed: `pip install -r requirements.txt`
- Check if port 8000 is free
- Delete `grievance.db` and reseed if database corrupted

### Frontend won't load
- Ensure Node 18+ installed
- Run `npm install` to install dependencies
- Check if port 5173 is free

### Emails not sending
- In mock mode: check backend console logs
- For real emails: verify SendGrid API key in `.env`
- Check spam folder

### Staff can't see grievances
- Verify staff user has correct `department_id`
- Check grievance is routed to their department

---

## Next Steps

1. Deploy to production (Docker/Kubernetes recommended)
2. Configure real email/SMS providers
3. Add more grievance categories specific to your institution
4. Customize escalation rules and SLA times
5. Integrate with your student information system (SIS)

---

**System Ready!** Start the backend and frontend, then visit http://localhost:5173 to begin.
