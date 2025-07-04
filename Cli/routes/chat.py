from flask import Flask, request
from pydantic import ValidationError

from schemas.chat import UserChatRequest, UserHistoryRequest, UserDecipherRequest
from services.chat import chat_service, history_service, decipher_service


def init_chat(app: Flask):

    @app.route("/chat", methods=["POST"])
    def chat():
        request_data = request.get_json()
        try:
            chat_data = UserChatRequest(**request_data)
        except ValidationError as e:
            return {"error": str(e)}, 400

        result, code = chat_service(
            friend_id=chat_data.data.friend_id,
            message=chat_data.data.message
        )
        return result, code

    @app.route("/history", methods=["POST"])
    def history():
        request_data = request.get_json()
        try:
            history_data = UserHistoryRequest(**request_data)
        except ValidationError as e:
            return {"error": str(e)}, 400

        result, code = history_service(
            friend_id=history_data.data.friend_id
        )
        return result, code

    @app.route("/decipher", methods=["POST"])
    def decipher():
        request_data = request.get_json()
        try:
            decipher_data = UserDecipherRequest(**request_data)
        except ValidationError as e:
            return {"error": str(e)}, 400

        result, code = decipher_service(
            timestamp=decipher_data.data.timestamp
        )
        return result, code