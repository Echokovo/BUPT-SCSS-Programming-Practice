from flask import Flask, jsonify
from flask import request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from ..schemas.contacts import AddFriendRequest, RemoveFriendRequest
from ..services.contacts import get_contacts_service, add_friend_service, remove_friend_service


def init_contacts(app: Flask):

    @app.route("/contacts", methods=["GET"])
    @jwt_required()
    def get_contacts():

        result = get_contacts_service(

        )

        return jsonify(result), result.get("status", 200)

    @app.route("/contacts", methods=["POST"])
    @jwt_required()
    def add_friend():
        request_data = request.get_json()
        try:
            add_friend_data = AddFriendRequest(**request_data)
        except ValidationError as e:
            return {"error": str(e)}, 400

        result = add_friend_service(

        )

        return jsonify(result), result.get("status", 200)

    @app.route("/contacts", methods=["DELETE"])
    @jwt_required()
    def remove_friend():
        request_data = request.get_json()
        try:
            remove_friend_data = RemoveFriendRequest(**request_data)
        except ValidationError as e:
            return {"error": str(e)}, 400

        result = remove_friend_service(

        )

        return jsonify(result), result.get("status", 200)