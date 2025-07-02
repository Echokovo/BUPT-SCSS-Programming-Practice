from database import db

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.String(64), primary_key=True)
    password = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False, unique=True)

    @classmethod
    def create_user(cls, user_id, password, email):
        user = cls(user_id=user_id, password=password, email=email)
        db.session.add(user)
        return user

    @classmethod
    def check_user(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first()
        return user

    @classmethod
    def check_password(cls, user_id, password):
        user = cls.query.filter_by(user_id=user_id).first()
        return user.password == password