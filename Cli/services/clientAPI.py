# p2p_client.py

import json
import socket
import threading
import base64
from queue import Queue, Empty

# Assuming you have a config file like this
# config.py
# CLIENT_CONFIG = {
#     'host': '127.0.0.1',
#     'port': 5001  # Example port
# }
# from config import CLIENT_CONFIG

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet


class ClientAPI:
    def __init__(self, host, port, user_id, public_key, private_key):
        self.host = host
        self.port = port
        self.user_id = user_id
        self.private_key = private_key
        self.public_key_pem = public_key

        # A thread-safe queue for incoming messages
        self.incoming_messages = Queue()

        # Start listening for messages in a background thread
        self.listener_thread = threading.Thread(target=self.start_listening, daemon=True)
        self.listener_thread.start()
        print(f"[*] P2P listener started on {host}:{port}")

    def start_listening(self):
        """
        Runs in a separate thread to listen for incoming connections without blocking.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # This allows you to restart the server quickly
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)

        while True:
            try:
                # Accept a new connection
                conn, addr = server_socket.accept()
                with conn:
                    # print(f"[*] Accepted connection from {addr}")
                    full_message = b""
                    while True:
                        data = conn.recv(4096)
                        if not data:
                            break
                        full_message += data

                    if full_message:
                        decrypted_message = self.decipher_message(full_message.decode('utf-8'))
                        # Put the decrypted message into the thread-safe queue
                        self.incoming_messages.put(decrypted_message)

            except Exception as e:
                print(f"[!] Error in listener thread: {e}")

    @classmethod
    def generate_key_pair(cls):
        """
        Generates an RSA private and public key pair.
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()

        # Serialize public key to PEM format to make it shareable
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return private_key, public_key_pem

    def generate_symmetric_key(self):
        """
        Generates a Fernet (AES-based) symmetric key.
        """
        return Fernet.generate_key()

    def cipher_by_public_key(self, message: bytes, public_key_pem: bytes) -> bytes:
        """
        Encrypts a message using a recipient's public key (PEM format).
        """
        public_key = serialization.load_pem_public_key(public_key_pem)
        ciphertext = public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext

    def decipher_by_private_key(self, ciphertext: bytes) -> bytes:
        """
        Decrypts a message using the instance's own private key.
        """
        plaintext = self.private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext

    def cipher_by_symmetric_key(self, message: str, symmetric_key: bytes) -> bytes:
        """
        Encrypts a string message using a symmetric key.
        """
        f = Fernet(symmetric_key)
        # Message must be in bytes
        return f.encrypt(message.encode('utf-8'))

    def decipher_by_symmetric_key(self, token: bytes, symmetric_key: bytes) -> str:
        """
        Decrypts a token using a symmetric key and returns a string.
        """
        f = Fernet(symmetric_key)
        decrypted_message_bytes = f.decrypt(token)
        return decrypted_message_bytes.decode('utf-8')

    def send_message(self, message: str, target_public_key_pem: bytes, target_host: str, target_port: int):
        """
        Sends a fully encrypted message to a target host/port.
        """
        try:
            # 1. Generate a one-time symmetric key
            symmetric_key = self.generate_symmetric_key()

            # 2. Encrypt the symmetric key with the recipient's public key
            encrypted_symmetric_key = self.cipher_by_public_key(symmetric_key, target_public_key_pem)

            # 3. Encrypt the actual message with the symmetric key
            encrypted_message = self.cipher_by_symmetric_key(message, symmetric_key)

            # 4. Prepare payload. Use base64 encoding for binary data in JSON.
            payload = {
                "user_id": self.user_id,
                "symmetric_key": base64.b64encode(encrypted_symmetric_key).decode('ascii'),
                "message": base64.b64encode(encrypted_message).decode('ascii')
            }
            payload_json = json.dumps(payload)

            # 5. Send the payload using a standard socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((target_host, target_port))
                s.sendall(payload_json.encode('utf-8'))

            print(f"[*] Message sent to {target_host}:{target_port}")
            return {"status": "success", "message": "Message sent successfully."}

        except Exception as e:
            print(f"[!] Failed to send message: {e}")
            return {"status": "error", "message": str(e)}

    def decipher_message(self, received_json: str) -> str:
        """
        Deciphers a complete incoming message payload.
        """
        # 1. Load the JSON payload
        message_data = json.loads(received_json)

        # 2. Decode base64 and decrypt the symmetric key
        encrypted_symmetric_key = base64.b64decode(message_data["symmetric_key"])
        symmetric_key = self.decipher_by_private_key(encrypted_symmetric_key)

        # 3. Decode base64 and decrypt the message
        encrypted_message = base64.b64decode(message_data["message"])
        result = self.decipher_by_symmetric_key(encrypted_message, symmetric_key)

        return result

    def get_latest_message(self):
        """
        A non-blocking method for the Flask app to retrieve received messages.
        """
        try:
            return self.incoming_messages.get_nowait()
        except Empty:
            return None


# --- Singleton Pattern Implementation ---

_client_api = None


def get_client_api(**kwargs):  # Provide default/config values
    global _client_api
    if _client_api is None:
        # This assumes CLIENT_CONFIG is available or you pass host/port
        # from config import CLIENT_CONFIG
        # _client_api = ClientAPI(host=CLIENT_CONFIG['host'], port=CLIENT_CONFIG['port'])
        _client_api = ClientAPI(**kwargs)
    return _client_api