from flask import Flask

from Server.config import init_config
from Server.routes.auth import init_auth
from Server.routes.contacts import init_contacts
from Server.routes.utils import init_utils



if __name__ == "__main__":
    app = Flask("app")
    init_config(app)
    init_auth(app)
    init_contacts(app)
    init_utils(app)
    app.run(debug=True)