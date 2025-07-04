from flask import Flask, jsonify
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from schemas.contacts import AddFriendRequest, DeleteFriendRequest
from services.contacts import get_contacts_service, add_friend_service, delete_friend_service


def init_contacts(app: Flask):

    @app.route("/contacts", methods=["GET"])
    @jwt_required()
    def get_contacts():
        user_id = get_jwt_identity()
        result, code = get_contacts_service(
            user_id=user_id
        )
        return result, code

    @app.route("/contacts", methods=["POST"])
    @jwt_required()
    def add_friend():
        user_id = get_jwt_identity()
        request_data = request.get_json()
        try:
            add_friend_data = AddFriendRequest(**request_data)
        except ValidationError as e:
            return {"error": str(e)}, 400

        result, code = add_friend_service(
            user_id=user_id,
            friend_id=add_friend_data.data.friend_id
        )
        return result, code

    @app.route("/contacts", methods=["DELETE"])
    @jwt_required()
    def remove_friend():
        user_id = get_jwt_identity()
        request_data = request.get_json()
        try:
            delete_friend_data = DeleteFriendRequest(**request_data)
        except ValidationError as e:
            return {"error": str(e)}, 400

        result, code = delete_friend_service(
            user_id=user_id,
            friend_id=delete_friend_data.data.friend_id
        )
        return result, code