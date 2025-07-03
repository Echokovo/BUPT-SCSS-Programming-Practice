from flask import Flask

CLIENT_CONFIG = {
    "listening_port": 50000
}

SERVER_CONFIG = {
    "host": "localhost:5000",
    "api_base": "",
    "timeout": 10
}

def init_config(app: Flask):
    pass