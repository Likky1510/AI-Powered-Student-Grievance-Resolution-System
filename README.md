# AI-Powered Student Grievance Resolution System

A multi-agent platform where students submit grievances, AI agents classify
and route them to the correct department, staff resolve and update status,
and admins see process-intelligence analytics (bottlenecks, SLA breaches,
escalation rates).

## Architecture

```
Student submits complaint
        │
        ▼
┌───────────────────────────────────────────┐
│ LangGraph Pipeline (app/agents/pipeline.py)│
│                                             │
│  Classification + Priority Agent (Claude)  │
│              │                             │
│              ▼                             │
│       Department Routing Agent             │
│   (rule-based lookup; Claude only for      │
│    genuinely ambiguous complaints)         │
└───────────────────────────────────────────┘
        │
        ▼
  Saved to Postgres, status = ASSIGNED
        │
        ▼
  Email notification sent (SendGrid)
        │
        ▼
  Staff updates status as work progresses
        │
        ▼
  Escalation Agent (APScheduler, every 30 min)
  checks SLA breaches → WhatsApp alert (Twilio)
        │
        ▼
  Analytics Agent: SQL aggregation + Claude
  summary → Admin dashboard
```

**Why some "agents" aren't separate LLM calls:** Department routing and
escalation are deterministic rule lookups/time comparisons. Running every
step through an LLM would add cost and latency with no accuracy benefit —
Claude is used only where judgment is genuinely required (classification,
priority assessment, ambiguous routing, and turning analytics numbers into
a readable summary).

## Tech stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, LangGraph, JWT auth
- **Frontend**: React + Vite, React Router, Recharts, Axios
- **AI**: Claude API (Anthropic)
- **Notifications**: SendGrid (email), Twilio (WhatsApp)
- **Scheduling**: APScheduler

## Quick start (Docker — recommended)

This is the easiest path since it handles Postgres for you.

1. **Set up environment variables:**
   ```bash
   cp backend/.env.example backend/.env
   ```
   Leave `ANTHROPIC_API_KEY`, `SENDGRID_API_KEY`, and `TWILIO_ACCOUNT_SID`
   as `mock` to run everything without real API keys — agents will use
   realistic simulated responses. Add real keys later with zero code changes.

2. **Start everything:**
   ```bash
   docker compose up --build
   ```

3. **Seed the database** (in a new terminal, once containers are up):
   ```bash
   docker compose exec backend python -m app.db.seed
   ```
   This creates departments and demo accounts (printed to console).

4. **Open the app:**
   - Frontend: http://localhost:5173
   - Backend API docs (Swagger): http://localhost:8000/docs

## Manual setup (without Docker)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

You'll need a local Postgres instance running, with `DATABASE_URL` in
`.env` pointing to it. Or, for the fastest possible local test without
installing Postgres, edit `.env`:
```
DATABASE_URL=sqlite:///./grievance.db
```
(SQLite works fine for development/demo purposes; switch to Postgres for
anything resembling production.)

Then:
```bash
python -m app.db.seed     # creates tables + demo accounts
uvicorn app.main:app --reload
```

API docs available at http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Opens at http://localhost:5173

## Demo accounts (created by the seed script)

| Role    | Email                      | Password   |
|---------|-----------------------------|------------|
| Admin   | admin@college.edu          | admin123   |
| Staff   | fees.staff@college.edu      | staff123   |
| Staff   | hostel.staff@college.edu    | staff123   |
| Student | student@college.edu        | student123 |

## Demo script (suggested order)

1. Log in as **student** → submit a complaint (try something urgent, e.g.
   mentioning a safety issue, vs. something routine) → show it gets
   auto-classified and routed differently.
2. Log in as the matching **staff** account → see it in the department
   queue, sorted by priority → update its status to `in_progress`, then
   `resolved`.
3. Log in as **student** again → view the case timeline → submit feedback.
4. Log in as **admin** → view analytics: department breakdown, AI-generated
   summary, and manually trigger an escalation check.

## Switching from mock mode to real APIs

Nothing in the code needs to change — just edit `backend/.env`:

- **Claude**: set `ANTHROPIC_API_KEY` to a real key from
  https://console.anthropic.com
- **SendGrid**: set `SENDGRID_API_KEY` and a verified `SENDGRID_FROM_EMAIL`
- **Twilio**: set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and a
  WhatsApp-enabled `TWILIO_WHATSAPP_FROM` number

Restart the backend after changing `.env`.

## Project structure

```
grievance-system/
├── backend/
│   ├── app/
│   │   ├── agents/          # All AI + rule-based agents
│   │   ├── core/            # Config, security, deps, scheduler
│   │   ├── db/               # DB session + seed script
│   │   ├── models/           # SQLAlchemy models + Pydantic schemas
│   │   ├── routers/          # API endpoints
│   │   └── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/               # Axios client + auth context
│   │   ├── components/        # Shared UI components
│   │   └── pages/             # Route pages
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## Known limitations / next steps

- Auth uses simple JWT, not Firebase — swap in Firebase Auth if your
  institution requires SSO with existing student accounts.
- `Base.metadata.create_all()` is used for schema setup (fine for a
  student project); use Alembic migrations for anything long-lived.
- The department routing "ambiguity" detector is a simple keyword check;
  could be made more robust if you see real-world misrouting.
- No automated test suite yet — add `pytest` + `httpx` test client tests
  for the routers if you want CI coverage.
