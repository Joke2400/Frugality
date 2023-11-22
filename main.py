"""The starting point for the app."""
import uvicorn
from dotenv import load_dotenv
from app.core import process

load_dotenv()

if __name__ == "__main__":
    app = process.Process()
    uvicorn.run(
        "main:process.app",
        host="0.0.0.0",
        port=80,
        log_level="info",
        reload=True,
        reload_includes="*"
    )
