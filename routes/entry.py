from fastapi import APIRouter

entry_root = APIRouter()

# Health check endpoint
@entry_root.get("/")
def api_running():
    res = {
        "status": "ok",
        "message": "API is running"
    }
    return res
