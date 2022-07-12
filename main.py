from core import app
from core.process import Process

if __name__ == "__main__":
    p = Process(web_app=app)
    p.start()

# Resources for the project

# GraphQL Serving over HTTP: https://graphql.org/learn/serving-over-http/
# HTTP Request Methods: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
# Connecting to GraphQL API: https://towardsdatascience.com/connecting-to-a-graphql-api-using-python-246dda927840


