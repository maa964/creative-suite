Plugin Store Authentication

1) Install dependencies:
   pip install -r requirements.txt
   pip install passlib[bcrypt] pyjwt

2) Create/update admin user:
   Use Python to hash a password and write to server/app/users_db.json, or run:
   python - <<'PY'
   from passlib.context import CryptContext
   import json
   from pathlib import Path
   p = Path('server/app/users_db.json')
   d = {}
   pwd = 'your_admin_password'
   from passlib.context import CryptContext
   pc = CryptContext(schemes=['bcrypt'], deprecated='auto')
   d['admin'] = {'username':'admin','full_name':'Administrator','hashed_password': pc.hash(pwd), 'scopes':['admin']}
   p.write_text(json.dumps(d, indent=2), encoding='utf-8')
   PY

3) Obtain JWT token (password grant):
   POST form to /token:
     curl -X POST -F "username=admin" -F "password=your_admin_password" http://localhost:8001/token

4) Use API Key:
   - Set environment variable CS_STORE_API_KEYS or edit server/app/config.py to include keys.
   - Call approve with header: X-API-Key: <your-key>
