from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from schemas.utils import GetStateRequest, GetPublicKeyRequest
from services.utils import online_service, public_key_service, heartbeat_service

def init_utils(app: Flask):

    @app.route("/online", methods=["POST"])
    @jwt_required()
    def online():
        user_id = get_jwt_identity()
        request_data = request.get_json()
        try:
            online_data = GetStateRequest(**request_data)
        except ValidationError as e:
            return {"error": str(e)}, 400

        result, code = online_service(
            user_id=user_id,
            friend_id=online_data.data.friend_id
        )
        return result, code

    @app.route("/public_key", methods=["POST"])
    @jwt_required()
    def public_key():
        user_id = get_jwt_identity()
        request_data = request.get_json()
        try:
            public_key_data = GetPublicKeyRequest(**request_data)
        except ValidationError as e:
            return {"error": str(e)}, 400

        result, code = public_key_service(
            user_id=user_id,
            friend_id=public_key_data.data.friend_id
        )
        return result, code

    @app.route("/heartbeat", methods=["GET"])
    @jwt_required()
    def heartbeat():
        user_id = get_jwt_identity()

        result, code = heartbeat_service(
            user_id=user_id
        )
        return result, code