CreativeStudio Plugin Store (prototype)


Includes:
 - FastAPI server skeleton (server/app)
 - signing utils using cryptography
 - admin CLI for signing manifests (cli/sign.py)

Quick start (dev):
  python -m pip install -r requirements.txt
  # run store server
  uvicorn server.app.main:app --reload --port 8001

Upload plugin (curl):
  curl -X POST "http://localhost:8001/plugins/upload" -F "manifest=@path/to/manifest.json" -F "package=@plugin.tar.gz"

Approve (server signs manifest):
  curl -X POST "http://localhost:8001/plugins/<name>/<version>/approve"

Download:
  curl -O "http://localhost:8001/plugins/<name>/<version>/download"

Signing CLI (admin):
  python cli/sign.py path/to/manifest.json

Security notes:
 - This is a prototype. In production, run behind HTTPS, require auth for approve, and use HSM/secure key storage.
