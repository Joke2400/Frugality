from core import process
# from temp.test import run

if __name__ == "__main__":
    # run()
    process.start(debug=True, reset=False)

    # TODO: Input sanitization will happen in validate_post(),
    # Flask I think has some funcs for that,
    # must be done before this gets hosted anywhere

    # TODO: Ensure that results contain string in QueryItem.must_contain

    # TODO: Logging
    # TODO: Typehints
    # TODO: Unittests
    # TODO: Database ofc
