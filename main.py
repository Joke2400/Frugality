"""The starting point for the app."""
import uvicorn
from dotenv import load_dotenv

from app.utils import LoggerManager
from app.core import Process

load_dotenv()
process = Process()

if __name__ == "__main__":
    uvicorn.run(
        "main:process.Process.app",
        host="0.0.0.0",
        port=80,
        log_level="info",
        reload=True,
        reload_includes="*"
    )
