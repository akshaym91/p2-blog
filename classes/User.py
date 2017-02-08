import random
import string
import hashlib
from google.appengine.ext import db


class User(db.Model):
    """
    User is a model class which has the following attributes
    name: name of the user
    hashed_password: Stores the hashed version of the password
    email: (Optional) Email ID of the user
    """

    name = db.StringProperty(required=True)
    hashed_password = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def user_key(cls, name='default'):
        return db.Key.from_path('User', name)

    @classmethod
    def make_salt(cls):
        return ''.join(random.choice(string.letters) for x in xrange(5))

    @classmethod
    def make_pw_hash(cls, name, pw, salt=""):
        if (salt == ""):
            salt = cls.make_salt()
        h = hashlib.sha256(name + pw + salt).hexdigest()
        return '%s|%s' % (h, salt)

    @classmethod
    def valid_pw(cls, name, pw, h):
        extracted_salt = h.split('|')[1]
        computed = cls.make_pw_hash(name, pw, extracted_salt)
        if (computed == h):
            return True

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid, parent=cls.user_key())

    @classmethod
    def by_name(cls, name):
        return cls.all().filter("name =", name).get()

    @classmethod
    def register(cls, name, password, email=None):
        hashed_password = cls.make_pw_hash(name, password)
        return User(parent=cls.user_key(),
                    name=name,
                    hashed_password=hashed_password,
                    email=email)

    @classmethod
    def retrieve(cls, name, password):
        user = cls.by_name(name)
        if user and cls.valid_pw(name, password, user.hashed_password):
            return user
