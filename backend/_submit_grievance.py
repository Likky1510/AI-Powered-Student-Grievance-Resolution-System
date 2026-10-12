import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

url = 'http://127.0.0.1:8001/grievances'
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNjk1NTBkNi0wMDBmLTQzZTctODExYy0wYTYyYzU0NGNjMTkiLCJyb2xlIjoic3R1ZGVudCIsImV4cCI6MTc4MjM3OTU3M30.7BhWzTrcq_pIDk2wyYpl7uxP4e5fFQuTxlHmi2yaxTw'
}
payload = {'raw_text': 'Test grievance: library book not available'}
req = Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
try:
    resp = urlopen(req)
    print(resp.read().decode())
except HTTPError as e:
    print('HTTP', e.code)
    print(e.read().decode())
except Exception as e:
    print('ERR', e)
