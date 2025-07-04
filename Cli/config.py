from flask import Flask

CLIENT_CONFIG = {
    "ip": "10.21.148.196",
    "port": 6000
}

SERVER_CONFIG = {
    "host": "localhost:5000",
    "api_base": "",
    "timeout": 10
}

def init_config(app: Flask):
    pass