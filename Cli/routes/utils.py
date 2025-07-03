from flask import Flask, request, jsonify
from pydantic import ValidationError

from schemas.utils import GetStateRequest
from services.utils import online_service

def init_utils(app: Flask):

    @app.route("/online", methods=["POST"])
    def online():
        request_data = request.get_json()
        try:
            online_data = GetStateRequest(**request_data)
        except ValidationError as e:
            return {"error": str(e)}, 400

        result, code = online_service(
            friend_id=online_data.data.friend_id
        )
        return result, code