from Server.models.database import db

class Contacts(db.Model):
    __tablename__ = 'contacts'
    __table_args__ = {"extend_existing": True}

    user_A = db.Column(db.String, db.ForeignKey('users.user_id'), primary_key=True)
    user_B = db.Column(db.String, db.ForeignKey('users.user_id'), primary_key=True)

    @classmethod
    def add_contact(cls, user_A, user_B):
        contact = cls(
            user_A=user_A,
            user_B=user_B
        )
        db.session.add(contact)
        db.session.commit()
        return contact

    @classmethod
    def check_contact(cls, user_A, user_B):
        contact = cls.query.filter_by(user_A=user_A, user_B=user_B).first()
        return contact is not None

    @classmethod
    def check_relationship(cls, user_A, user_B):
        return cls.check_contact(user_A, user_B) and cls.check_contact(user_B, user_A)

    @classmethod
    def delete_contact(cls, user_A, user_B):
        contact = cls.query.filter_by(user_A=user_A, user_B=user_B).first()
        db.session.delete(contact)
        db.session.commit()
        return contact

    @classmethod
    def get_all_contacts(cls, user_id):
        contact = cls.query.filter(
            (cls.user_A == user_id) | (cls.user_B == user_id)
        ).all()
        return contact

    @classmethod
    def get_contacts_by_A(cls, user_A):
        contacts = cls.query.filter_by(user_A=user_A).all()
        return contacts

    @classmethod
    def get_contacts_by_B(cls, user_B):
        contacts = cls.query.filter_by(user_B=user_B).all()
        return contacts