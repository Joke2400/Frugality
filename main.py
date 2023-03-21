from core import process

if __name__ == "__main__":
    process.start(debug=False, reset=False)

    # TODO: Put these todos in my notebook...
    # TODO: Product filtering functionality (not present)
    # TODO: Database for caching purposes
    # TODO: Security considerations, private key, potential gmaps key etc etc
    # TODO: Tests are in an even more worthless state than before...
    # TODO: Change the logic of LoggerManager so that __init__.py doesn't
    # need it's own call to LoggerManager before the module loggers
    # TODO: Rework how flask app is instantiated, Process class also needs to
    # be a singleton
    # TODO: Rework the damn imports/program structure, they're garbage
    # TODO: Some functions need logging