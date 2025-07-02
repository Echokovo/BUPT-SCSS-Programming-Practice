from flask import Flask

from config import init_config
from routes.auth import init_auth
from routes.contacts import init_contacts
from routes.utils import init_utils


if __name__ == "__main__":
    app = Flask("app")
    init_config(app)
    init_auth(app)
    init_contacts(app)
    init_utils(app)
    app.run(debug=True)