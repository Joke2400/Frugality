"""The starting point for the app."""
from app.core import process

fastapi = process.Process()

if __name__ == "__main__":
    fastapi.startup()