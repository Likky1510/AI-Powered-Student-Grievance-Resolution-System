import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

url = 'http://127.0.0.1:8000/auth/register'
payload = {
    'name': 'Temp User',
    'email': 'temp.user@local.test',
    'password': 'temppass',
    'role': 'student'
}
req = Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
try:
    resp = urlopen(req)
    print(resp.read().decode())
except HTTPError as e:
    print('HTTP', e.code)
    print(e.read().decode())
except Exception as e:
    print('ERR', e)
