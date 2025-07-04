from flask import Flask
from flask_cors import CORS

from routes.auth import init_auth
from routes.chat import init_chat
from routes.contacts import init_contacts
from routes.utils import init_utils


def create_app():
    ret = Flask(__name__)
    init_auth(ret)
    init_contacts(ret)
    init_utils(ret)
    init_chat(ret)
    return ret

def create_app_debug():
    ret = Flask(__name__)
    init_auth(ret)
    init_contacts(ret)
    init_utils(ret)
    init_chat(ret)
    cors = CORS(ret, resources=r"/*")
    return ret

app = create_app_debug()

if __name__ == "__main__":
    app.run(port=50000,debug=True)