from flask import Flask

from config import init_config
from routes.auth import init_auth
from routes.contacts import init_contacts
from routes.utils import init_utils



def create_app():
    from models.database import db
    from models.users import User
    from models.contacts import Contacts
    from models.online import Online
    app = Flask(__name__)
    init_config(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    init_auth(app)
    init_contacts(app)
    init_utils(app)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)