from core import process

if __name__ == "__main__":
    process.start(debug=True, reset=False)

    # TODO: Put these todos in my notebook...
    # TODO: Product filtering functionality (not present)
    # TODO: Database for caching purposes
    # TODO: Security considerations, private key, potential gmaps key etc etc
    # TODO: Tests are in an even more worthless state than before...
    # TODO: Rest of the docstrings for finalized funcs
    # TODO: Docstrings
    # TODO: Imports need to be reorganized, Process class needs to be a singleton
    # TODO: The way the flask app is instantiated makes imports stupid.
    # TODO: Change the logic of LoggerManager so that __init__.py doesn't
    # need it's own call to LoggerManager before the module loggers