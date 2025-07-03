from flask import Flask, jsonify
from flask import request
from pydantic import ValidationError

from schemas.contacts import AddFriendRequest, DeleteFriendRequest
from services.contacts import get_contacts_service, add_friend_service, delete_friend_service, agree_service


def init_contacts(app: Flask):

    @app.route("/contacts", methods=["GET"])
    def get_contacts():
        result, code = get_contacts_service()
        return result, code

    @app.route("/contacts", methods=["POST"])
    def add_friend():
        request_data = request.get_json()
        try:
            add_friend_data = AddFriendRequest(**request_data)
        except ValidationError as e:
            return {"error": str(e)}, 400

        result, code = add_friend_service(
            friend_id=add_friend_data.data.friend_id
        )
        return result, code

    @app.route("/agree", methods=["POST"])
    def agree():
        result, code = agree_service(

        )
        return result, code

    @app.route("/contacts", methods=["DELETE"])
    def remove_friend():
        request_data = request.get_json()
        try:
            delete_friend_data = DeleteFriendRequest(**request_data)
        except ValidationError as e:
            return {"error": str(e)}, 400

        result, code = delete_friend_service(
            friend_id=delete_friend_data.data.friend_id
        )
        return result, code