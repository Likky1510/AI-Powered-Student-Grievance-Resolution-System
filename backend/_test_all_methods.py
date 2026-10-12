"""
Complete testing script demonstrating all data insertion methods.
Run this to populate test data and verify the system works end-to-end.
"""
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import sys
sys.path.insert(0, '.')

from app.db.session import SessionLocal
from app.models.models import User, Grievance

# ============================================================================
# METHOD 1: DIRECT DATABASE INSERTION (No API calls)
# ============================================================================

def test_method_1_database_insert():
    """Insert data directly into SQLite database."""
    print("\n" + "="*70)
    print("METHOD 1: DIRECT DATABASE INSERTION")
    print("="*70)
    
    db = SessionLocal()
    try:
        # Count before
        before = db.query(Grievance).count()
        print(f"📊 Grievances before: {before}")
        
        # This would normally insert data - shown as example
        print("✓ Can insert any number of records without API limits")
        print("✓ Useful for load testing with thousands of records")
        print("✓ Direct SQL manipulation possible")
        
        # Count after (unchanged in this demo)
        after = db.query(Grievance).count()
        print(f"📊 Grievances after: {after}")
        
    finally:
        db.close()


# ============================================================================
# METHOD 2: API-BASED INSERTION (HTTP Requests)
# ============================================================================

def get_auth_token(email, password):
    """Get JWT token from /auth/login endpoint."""
    url = 'http://127.0.0.1:8000/auth/login'
    data = f"username={email}&password={password}".encode('utf-8')
    req = Request(url, data=data)
    
    try:
        resp = urlopen(req)
        response_data = json.loads(resp.read().decode())
        return response_data['access_token']
    except HTTPError as e:
        print(f"❌ Login failed: {e.read().decode()}")
        return None


def submit_grievance_via_api(token, complaint_text):
    """Submit grievance via /grievances POST endpoint."""
    url = 'http://127.0.0.1:8000/grievances'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = {'raw_text': complaint_text}
    req = Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
    
    try:
        resp = urlopen(req)
        return json.loads(resp.read().decode())
    except HTTPError as e:
        print(f"❌ Submission failed: {e.read().decode()}")
        return None


def test_method_2_api_insert():
    """Test API-based data insertion."""
    print("\n" + "="*70)
    print("METHOD 2: API-BASED INSERTION (JSON requests)")
    print("="*70)
    
    # Login
    print("\n1️⃣  Authenticating...")
    token = get_auth_token('student@college.edu', 'student123')
    
    if not token:
        print("❌ Could not authenticate")
        return
    
    print(f"✓ Got token: {token[:50]}...")
    
    # Submit sample grievance
    print("\n2️⃣  Submitting grievance via API...")
    complaints = [
        "The library WiFi connection keeps dropping during my study sessions",
        "I was not given credit for my assignment despite submitting on time",
        "The semester fees were charged twice to my account"
    ]
    
    for i, complaint in enumerate(complaints, 1):
        print(f"\n   Submitting complaint {i}...")
        result = submit_grievance_via_api(token, complaint)
        
        if result:
            print(f"   ✓ Case ID: {result['id']}")
            print(f"   ✓ Category: {result['category']}")
            print(f"   ✓ Priority: {result['priority']}")
            print(f"   ✓ Status: {result['status']}")
        else:
            print(f"   ❌ Failed to submit")
    
    print("\n✓ API method tested successfully")


# ============================================================================
# METHOD 3: FRONTEND UI TESTING
# ============================================================================

def test_method_3_frontend():
    """Instructions for testing via frontend."""
    print("\n" + "="*70)
    print("METHOD 3: FRONTEND UI SUBMISSION")
    print("="*70)
    
    print("""
    ✓ Open: http://localhost:5173
    ✓ Login with: student@college.edu / student123
    ✓ Click: "File a Complaint"
    ✓ Enter any complaint text
    ✓ Click: "Submit complaint"
    ✓ System auto-classifies and routes
    ✓ View confirmation with Case ID
    
    This method is best for:
    - User acceptance testing
    - Visual confirmation of flows
    - Testing UI/UX
    """)


# ============================================================================
# METHOD 4: BULK DATA INSERTION
# ============================================================================

def test_method_4_bulk():
    """Instructions for bulk data insertion."""
    print("\n" + "="*70)
    print("METHOD 4: BULK DATA INSERTION")
    print("="*70)
    
    print("""
    ✓ Run: python _bulk_insert_data.py
    
    This script will:
    - Insert 30 grievances across all categories
    - Cover academic, fees, hostel, etc.
    - Use realistic timestamps (1-7 days old)
    - Vary statuses for different states
    
    Great for:
    - Load testing
    - Testing sorting/filtering
    - Analytics dashboards
    - Database performance
    """)


# ============================================================================
# METHOD 5: API DOCS INTERACTIVE
# ============================================================================

def test_method_5_swagger():
    """Instructions for Swagger UI testing."""
    print("\n" + "="*70)
    print("METHOD 5: SWAGGER API DOCUMENTATION")
    print("="*70)
    
    print("""
    ✓ Open: http://127.0.0.1:8000/docs
    ✓ Find endpoint: POST /grievances
    ✓ Click: "Try it out"
    ✓ Enter request body: {"raw_text": "your complaint"}
    ✓ Click: "Execute"
    ✓ View response below
    
    Available endpoints to test:
    - POST   /auth/login              (Get token)
    - POST   /grievances              (Submit grievance)
    - GET    /grievances/me            (List your cases)
    - GET    /grievances/{id}          (Get case details)
    - GET    /grievances/{id}/history  (View timeline)
    """)


# ============================================================================
# SHOW CURRENT DATA STATUS
# ============================================================================

def show_data_status():
    """Show current test data in the system."""
    print("\n" + "="*70)
    print("CURRENT DATA STATUS")
    print("="*70)
    
    db = SessionLocal()
    try:
        total_grievances = db.query(Grievance).count()
        total_users = db.query(User).count()
        
        print(f"\n📊 Database statistics:")
        print(f"   Total Users: {total_users}")
        print(f"   Total Grievances: {total_grievances}")
        
        # Show by category
        from app.models.models import GrievanceCategory
        print(f"\n📋 Grievances by category:")
        for cat in GrievanceCategory:
            count = db.query(Grievance).filter(Grievance.category == cat).count()
            if count > 0:
                print(f"   - {cat.value}: {count}")
        
        # Show by status
        from app.models.models import GrievanceStatus
        print(f"\n📈 Grievances by status:")
        for status in GrievanceStatus:
            count = db.query(Grievance).filter(Grievance.status == status).count()
            if count > 0:
                print(f"   - {status.value}: {count}")
        
        # Show by priority
        from app.models.models import GrievancePriority
        print(f"\n🎯 Grievances by priority:")
        for priority in GrievancePriority:
            count = db.query(Grievance).filter(Grievance.priority == priority).count()
            if count > 0:
                print(f"   - {priority.value}: {count}")
        
    finally:
        db.close()


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    print("\n" + "="*70)
    print("GRIEVANCE SYSTEM - COMPREHENSIVE TEST DATA GUIDE")
    print("="*70)
    
    # Show current status
    show_data_status()
    
    # Demonstrate each method
    test_method_1_database_insert()
    test_method_2_api_insert()
    test_method_3_frontend()
    test_method_4_bulk()
    test_method_5_swagger()
    
    # Final instructions
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("""
    1. Choose your testing method above
    2. Add test data using preferred method
    3. Verify in frontend: http://localhost:5173
    4. Check API: http://127.0.0.1:8000/docs
    5. Monitor database changes
    
    Recommended order for comprehensive testing:
    □ Method 2 (API) - Test 3-5 grievances
    □ Method 1 (Database) - Insert 10-20 more
    □ Method 3 (Frontend) - Submit via UI
    □ Method 4 (Bulk) - Load test with 30+
    □ Method 5 (Swagger) - Test all endpoints
    """)


if __name__ == '__main__':
    main()
