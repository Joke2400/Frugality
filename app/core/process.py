"""Contains a process singleton class for managing the application."""


from fastapi import FastAPI, Response


class Process():

    app: FastAPI = FastAPI()

    def __init__(self, **kwargs):
        print("hello")
        pass


app = Process.app


@app.get("/")
def read_root():
    return Response("This is a test")
