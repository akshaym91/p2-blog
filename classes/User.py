from google.appengine.ext import db


class User(db.Model):
    """docstring for User"""

    name = db.StringProperty(required=True)
    hashed_password = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid, parent=user_key())

    @classmethod
    def by_name(cls, name):
        return cls.all().filter("name =", name).get()

    @classmethod
    def register(cls, name, password, email=None):
        hashed_password = make_pw_hash(name, password)
        return User(parent=user_key(),
                    name=name,
                    hashed_password=hashed_password,
                    email=email)

    @classmethod
    def retrieve(cls, name, password):
        user = cls.by_name(name)
        if user and valid_pw(name, password, user.hashed_password):
            return user
