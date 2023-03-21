from core import flask_app as app

if __name__ == "__main__":
    # VERY IMPORTANT: APP SECRET KEY IS SET TO HARDCODED DEFAULT
    # IMPORT KEY FROM .TXT FILE BEFORE HOSTING
    app.run(debug=True)

    # TODO: Put these todos in my notebook...
    # TODO: Product filtering functionality (not present)
    # TODO: Database for caching purposes
    # TODO: Security con<siderations, private key, potential gmaps key etc etc
    # TODO: Tests are in an even more worthless state than before...
    # TODO: Change the logic of LoggerManager so that __init__.py doesn't
    # need it's own call to LoggerManager before the module loggers
    # TODO: Rework how flask app is instantiated, Process class also needs to
    # be a singleton
    # TODO: Rework the damn imports/program structure, they're garbage
    # TODO: Some functions need logging