from flask import Flask
from flask_cors import CORS

from routes.auth import init_auth
from routes.chat import init_chat
from routes.contacts import init_contacts
from routes.utils import init_utils


def create_app():
    app = Flask(__name__)
    CORS(app)
    init_auth(app)
    init_contacts(app)
    init_utils(app)
    init_chat(app)
    return app

def create_app_debug():
    app = Flask(__name__)

    init_auth(app)
    init_contacts(app)
    init_utils(app)
    init_chat(app)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888,debug=False)