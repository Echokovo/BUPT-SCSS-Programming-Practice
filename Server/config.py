from flask import Flask


def init_config(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:DIGKEHFC@localhost'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False