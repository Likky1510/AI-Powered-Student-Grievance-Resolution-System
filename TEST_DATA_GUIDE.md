# TEST DATA INSERTION GUIDE
# Complete walkthrough: Frontend, API, and Database

## METHOD 1: VIA FRONTEND UI (Easiest for Students)
## ============================================

URL: http://localhost:5173
Login: student@college.edu / student123

Steps:
1. Navigate to "File a Complaint" 
2. Enter complaint text in the textarea
3. Click "Submit complaint"
4. System auto-classifies and routes the grievance
5. See confirmation with Case ID

Example Complaint Texts to Test:
- "My exam results are still not published" (→ category: academic)
- "The hostel AC is broken" (→ category: hostel)
- "I was charged twice for the semester fee" (→ category: fees)
- "WiFi in library is not working" (→ category: infrastructure)


## METHOD 2: VIA API ENDPOINTS (For Automation/Testing)
## ====================================================

### Step 1: Get Authentication Token
-----------
POST /auth/login

Command:
  curl -X POST -d "username=student@college.edu&password=student123" \\
    http://127.0.0.1:8000/auth/login

Response:
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {...}
  }

Copy the access_token value for next steps.


### Step 2: Submit a Grievance via API
-----------
POST /grievances

Command:
  curl -X POST \\
    -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
    -H "Content-Type: application/json" \\
    -d '{"raw_text":"Library books are not available on shelf"}' \\
    http://127.0.0.1:8000/grievances

Response:
  {
    "id": "abc123xyz",
    "student_id": "user_id",
    "raw_text": "Library books are not available on shelf",
    "category": "other",
    "priority": "low",
    "status": "assigned",
    "created_at": "2026-06-24T10:15:30"
  }


### Step 3: List Your Grievances
-----------
GET /grievances/me

Command:
  curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
    http://127.0.0.1:8000/grievances/me

Response: [List of all your submitted grievances]


### Step 4: Get Specific Grievance Details
-----------
GET /grievances/{grievance_id}

Command:
  curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
    http://127.0.0.1:8000/grievances/abc123xyz

Response: [Full grievance object with all fields]


## METHOD 3: VIA DATABASE SCRIPT (Direct Data Insertion)
## =====================================================

Create a Python script to insert bulk test data directly.
File: backend/_bulk_insert_data.py

Usage:
  python _bulk_insert_data.py

This method:
- Bypasses the API pipeline
- Directly creates records in SQLite
- Useful for load testing with large datasets
- Allows inserting with specific statuses/timestamps


## METHOD 4: VIA API DOCS INTERACTIVE INTERFACE
## ============================================

URL: http://127.0.0.1:8000/docs

Steps:
1. Open the Swagger UI
2. Click on any endpoint (e.g., POST /grievances)
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"
6. View response directly in the UI

This is perfect for:
- Learning the API
- Quick manual testing
- Exploring all available endpoints


## TEST DATA SAMPLES BY CATEGORY
## =============================

ACADEMIC:
  "I did not receive my exam marks yet"
  "My attendance was marked wrong"
  "Professor declined my attendance condonation"

FEES:
  "I was overcharged for hostel fees"
  "Scholarship disbursement is delayed"
  "Refund for dropped course not processed"

HOSTEL:
  "AC in my room is not working"
  "Mess food quality is poor"
  "Internet connectivity in hostel is down"

CERTIFICATES:
  "I need a bonafide certificate urgently"
  "Transcript request is still pending"
  "Migration certificate not issued"

INFRASTRUCTURE:
  "Library WiFi keeps disconnecting"
  "Computer lab equipment is broken"
  "Water supply issue in building A"

ATTENDANCE:
  "My attendance record is incorrect"
  "Unable to apply for condonation"
  "Excess absences blocking me from exams"

OTHER:
  [Any complaint that doesn't fit above categories]


## EXPECTED SYSTEM BEHAVIOR
## =========================

When you submit a grievance:

1. Classification Agent analyzes text
   → Determines category (academic, fees, etc.)
   → Assigns priority (low, medium, high, urgent)

2. Routing Agent selects department
   → Maps category to responsible department
   → Sets status to "assigned"

3. Status History Records
   → created -> submitted -> categorized -> assigned

4. Timeline Updates
   → All changes logged with timestamps
   → Accessible via /grievances/{id}/history


## INTERACTIVE TESTING CHECKLIST
## =============================

□ Submit 5 grievances via frontend UI (different categories)
□ Check "My Cases" page - all 5 appear in table
□ Click "View timeline" - see status progression
□ Login as staff (fees.staff@example.com/staffpass)
□ Check department queue - see only fees grievances
□ Submit grievance via API using curl
□ List grievances via API - verify new one appears
□ Get specific grievance by ID via API
□ Open /docs and test endpoints interactively
□ Filter by status (submitted, assigned, in_progress)
□ Test all role-based access (student vs staff vs admin)
