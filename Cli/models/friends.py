from database import friends_db, query

class Friends():

    def __init__(self):
        self.db = friends_db
        self.table = friends_db.table('friends')


    def create_friend(self, friend_id, public_key, ip, port):
        self.table.insert({
            friend_id: friend_id,
            public_key: public_key,
            ip: ip,
            port: port
        })

    def get_friend(self, friend_id):
        result = self.table.search(
            query.friend_id == friend_id
        )
        return result

    def check_friend(self, friend_id):
        result = self.table.search(
            query.friend_id == friend_id
        )
        if result:
            return True
        else:
            return False

    def delete_friend(self, friend_id):
        self.db.remove(
            query.friend_id == friend_id
        )

friends = Friends()