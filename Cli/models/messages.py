from database import messages_db, query

class Messages():

    def __init__(self):
        self.db = messages_db
        self.table = messages_db.table('messages')

    def insert_message(self, message):
        self.db.insert(**message)

    def get_message_by_sender_id(self, sender_id):
        result = self.table.search(
            query.sender_id == sender_id
        )
        return result

    def get_messages_by_receiver_id(self, receiver_id):
        result = self.table.search(
            query.receiver_id == receiver_id
        )
        return result

    def get_message_by_timestamp(self, timestamp):
        result = self.table.search(
            query.timestamp == timestamp
        )
        return result

messages = Messages()