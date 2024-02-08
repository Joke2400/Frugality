"""The starting point for the app."""
import uvicorn
from backend.app.core import process

fastapi = process.Process()

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:fastapi.app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
        reload=True,
        reload_includes="*.py"
    )
