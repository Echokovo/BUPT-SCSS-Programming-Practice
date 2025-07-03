from flask import Flask
from flask_jwt_extended import JWTManager

from config import init_config
from routes.auth import init_auth
from routes.contacts import init_contacts
from routes.utils import init_utils
from services.online import CheckUser


def create_app():
    from models.database import db
    app = Flask(__name__)
    init_config(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    jwt = JWTManager(app)
    init_auth(app)
    init_contacts(app)
    init_utils(app)
    check_user = CheckUser(app)
    return app

def create_app_debug():
    from models.database import db
    app = Flask(__name__)
    app.config.update({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })
    db.init_app(app)
    with app.app_context():
        db.create_all()
    jwt = JWTManager(app)
    init_auth(app)
    init_contacts(app)
    init_utils(app)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=False)