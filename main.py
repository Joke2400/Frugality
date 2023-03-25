from core import flask_app as app

if __name__ == "__main__":
    # VERY IMPORTANT: APP SECRET KEY IS SET TO HARDCODED DEFAULT
    # IMPORT KEY FROM .TXT FILE BEFORE HOSTING
    app.run(debug=True)

    todos = """
    TODO: NEXT-UP; SQLITE DATABASE -> PRODUCT DATA CACHING | DATA COLLECTION FOR FUTURE PRICE STATISTICS

    TODO: Product filtering functionality is still not present. Implementation details still unclear.
    Whether to do everything just in JS or to create some backend funcs aswell.

    TODO: SETTINGS file, flask private-key.txt, FUTURE Gmaps Tokens.txt etc etc

    TODO: LoggerManager -> Move away from the classmethods approach and just use a singleton class for
    easier configuration of loggers.

    TODO: DOCSTRINGS, some functions might still lack adequate logging...
    """
