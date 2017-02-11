from google.appengine.ext import db


class Like(db.Model):
    """
    Like is a model class which has the following attributes
    post_id: The associted posts's id
    username: Author of the like
    created: Timestamp of the creation of teh like
    """
    post_id = db.IntegerProperty(required=True)
    username = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def by_name(cls, name):
        return cls.all().filter("username =", name).get()
