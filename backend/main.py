"""The starting point for the app."""
import sys
import uvicorn
from dotenv import load_dotenv
from backend.app.core import process

# Get the arg that the dockerfile passes in, used to set the correct DB url
# This code will probably be moved elsewhere/improved
CONTAINER = False
for arg in sys.argv[1:]:
    if "--container" in arg:
        if arg.split("=")[1] in ("True", "true"):
            CONTAINER = True
            break

load_dotenv()
app = process.Process(in_container=CONTAINER)

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app.app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
        reload=True,
        reload_includes="*.py"
    )
