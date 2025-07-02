from flask import Flask, jsonify
from flask import request
from pydantic import ValidationError

from ..schemas.auth import UserRegisterRequest, UserLoginRequest
from ..services.auth import register_service, login_service

def init_auth(app: Flask):

    @app.route("/register", methods=["POST"])
    def register():
        request_data = request.get_json()
        try:
            register_data = UserRegisterRequest(**request_data)
        except ValidationError as e:
            return {"error": str(e)}, 400

        result = register_service(
            user_id=register_data.user_id,
            password=register_data.password,
            email=register_data.email
        )

        return jsonify(result), result.get("status", 200)

    @app.route("/login", methods=["POST"])
    def login():
        request_data = request.get_json()
        try:
            login_data = UserLoginRequest(**request_data)
        except ValidationError as e:
            return {"error": str(e)}, 400

        result = login_service(
            user_id=login_data.user_id,
            password=login_data.password,
            public_key=login_data.public_key,
            ip=login_data.ip,
            port=login_data.port
        )

        return jsonify(result), result.get("status", 200)