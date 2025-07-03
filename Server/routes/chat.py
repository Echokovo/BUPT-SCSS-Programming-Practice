from flask import Flask

from services.chat import chat_service, history_service, decipher_service


def init_chat(app: Flask):

    @app.route("/chat", methods=["POST"])
    def chat():
        result, code = chat_service(

        )
        return result, code

    @app.route("/history", methods=["POST"])
    def history():
        result, code = history_service(

        )
        return result, code

    @app.route("/decipher", methods=["POST"])
    def decipher():
        result, code = decipher_service(

        )
        return result, code