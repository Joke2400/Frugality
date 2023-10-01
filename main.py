"""The starting point for the app."""
import uvicorn

from app.core import Process

process = Process()

if __name__ == "__main__":
    uvicorn.run(
        "main:process.app",
        host="0.0.0.0",
        port=80,
        log_level="info",
        reload=True,
        reload_includes="*"
    )
