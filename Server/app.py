from flask import Flask

from routes.auth import init_auth
from routes.contacts import init_contacts
from routes.utils import init_utils


def create_app():
    app = Flask(__name__)

    init_auth(app)
    init_contacts(app)
    init_utils(app)
    return app

def create_app_debug():
    app = Flask(__name__)

    init_auth(app)
    init_contacts(app)
    init_utils(app)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=False)