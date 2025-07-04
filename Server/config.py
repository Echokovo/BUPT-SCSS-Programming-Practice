from datetime import timedelta

from flask import Flask

TIME_TO_LIVE = timedelta(seconds=600)

def init_config(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:DIGKEHFC@localhost:3306/test3"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'test'