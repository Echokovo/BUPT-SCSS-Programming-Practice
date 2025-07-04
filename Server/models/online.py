from datetime import datetime

from models.database import db

class Online(db.Model):
    __tablename__ = 'online'
    __table_args__ = {"extend_existing": True}

    user_id = db.Column(db.String(64), db.ForeignKey('users.user_id'), primary_key=True)
    public_key = db.Column(db.String(512), nullable=False)
    ip = db.Column(db.String(64), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    last_seen_time = db.Column(db.DateTime, nullable=False, default=datetime.now())

    @classmethod
    def user_login(cls, user_id, public_key, ip, port):
        user = cls(
            user_id=user_id,
            public_key=public_key,
            ip=ip,
            port=port
        )
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def update_last_seen(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first()
        user.last_seen_time = datetime.now()
        db.session.commit()
        return user

    @classmethod
    def user_logout(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        return user

    @classmethod
    def get_user(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first()
        return user

    @classmethod
    def get_state(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first()
        if user is None:
            return None
        return True

    @classmethod
    def delete_inactive_user(cls, time_to_live):
        users = cls.query.filter(
            cls.last_seen_time < time_to_live
        ).all()
        for user in users:
            db.session.delete(user)
        db.session.commit()
        return users