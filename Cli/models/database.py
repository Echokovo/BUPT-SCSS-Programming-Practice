from tinydb import TinyDB, Query

friends_db = TinyDB('friends.db')
messages_db = TinyDB('messages.db')
query = Query()