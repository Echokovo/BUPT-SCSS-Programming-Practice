from database import messages_db, query

class Messages():

    def __init__(self):
        self.db = messages_db
        self.table = messages_db.table('messages')

    def insert_message(self, message):
        self.db.insert(**message)

    def get_message(self, timestamp):
        result = self.table.search(
            query.timestamp == timestamp
        )
        return result

messages = Messages()