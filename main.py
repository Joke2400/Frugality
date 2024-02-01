"""The starting point for the app."""
import sys
import uvicorn
from dotenv import load_dotenv
from app.core import process

# Get the arg that the dockerfile passes in
# This code will probably be moved elsewhere
container = False
for arg in sys.argv[1:]:
    if "--container" in arg:
        if arg.split("=")[1] in ("True", "true"):
            container = True
            break
print(container)

load_dotenv()
app = process.Process(in_container=container)

if __name__ == "__main__":
    uvicorn.run(
        "main:app.app",
        host="0.0.0.0",
        port=80,
        log_level="info",
        reload=True,
        reload_includes="*"
    )
