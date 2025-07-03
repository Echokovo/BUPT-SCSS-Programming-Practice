from flask import Flask


def init_config(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:DIGKEHFC@localhost:3306/test2"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'test'