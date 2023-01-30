from core import process
# from temp import run

if __name__ == "__main__":
    # run()
    process.start(debug=True, reset=False)

    # TODO: Put these todos in my notebook...
    # TODO: add more units to regex_get_quantity
    # TODO: Product filtering functionality should be a lot more robust
    # TODO: HTTP errorcodes handling
    # TODO: Store validation/get funcs logging
    # TODO: Refactor old code to use match case syntax where appropriate
    # TODO: Use firefox debugger extens. so that debugging js in firefox works correctly
    # TODO: Database, store data, product data storage
    # TODO: Security considerations, private key
    # https://flask.palletsprojects.com/en/2.2.x/security/
    # TODO: If store not found, request user for re-input <- This flow is missing
    # TODO: IMPORTANT, frontend currently doesnt receive products and is 
    # also unable to display them on the page
    # TODO: Basic response embed on frontend for debugging
    # TODO: OPTIMIZE, program flow could be simplified.
    # TODO: Rework app classes again........ because i made way too many separate classes and it's hard to read and probably not very performant
    # TODO: The first GraphQL response was very slow after i hadn't sent a request for a month, start using persisted queries when appropriate
    # TODO: Tests are broken again...
    # TODO: app.py "query()" function is too long and needs to be split