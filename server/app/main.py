from fastapi import FastAPI

from .plugins import router as plugin_router
from .dashboard import router as dashboard_router

app = FastAPI(title="CreativeStudio Plugin Store API")

try:
    app.include_router(auth_router)
except Exception as e:
    print(f"Error including auth_router: {e}")

try:
    app.include_router(plugin_router)
except Exception as e:
    print(f"Error including plugin_router: {e}")

try:
    app.include_router(dashboard_router)
except Exception as e:
    print(f"Error including dashboard_router: {e}")

# TODO: Add tests to verify the functionality of the API
# TODO: Verify results by running the API and testing the endpoints
