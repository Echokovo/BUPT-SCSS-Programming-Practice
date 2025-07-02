from database import db

class Online(db.Model):
    __tablename__ = 'online'

    user_id = db.Column(db.String(64), primary_key=True)
    state = db.Column(db.Boolean, nullable=False)
    public_key = db.Column(db.String(64), nullable=False)
    ip = db.Column(db.String(64), nullable=False)
    port = db.Column(db.Integer, nullable=False)

    @classmethod
    def user_login(cls, user_id, public_key, ip, port):
        user = cls.query.filter_by(user_id=user_id).first()
        if user is None:
            user = cls(user_id=user_id, state=True, public_key=public_key, ip=ip, port=port)
        else:
            user.public_key = public_key
            user.ip = ip
            user.port = port
        db.session.add(user)
        return user

    @classmethod
    def user_logout(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first()
        if user is None:
            raise Exception("User not found")
        user.state = False
        db.session.add(user)
        return user