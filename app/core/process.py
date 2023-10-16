"""Contains a process singleton class for managing the application."""


from fastapi import FastAPI, Response
from ..api.routes import router

class Process():

    app: FastAPI = FastAPI()

    def __init__(self, **kwargs):
        self.app.include_router(router)

app = Process.app


@app.get("/")
def read_root():
    return Response("This is a test")
