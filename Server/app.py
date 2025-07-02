from flask import Flask

from config import init_config
from routes.auth import init_auth
from routes.contacts import init_contacts
from routes.utils import init_utils
from models.users import User
from models.contacts import Contacts
from models.online import Online
from models.database import init_db

app = Flask(__name__)

if __name__ == "__main__":
    init_config(app)
    init_db(app)
    init_auth(app)
    init_contacts(app)
    init_utils(app)
    app.run(debug=True)