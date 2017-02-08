from google.appengine.ext import db


class Comment(db.Model):
    """
    Comment is a model class which has the following attributes
    post_id: The associted posts's id
    username: Author of the comment
    comment: Content of the comment
    created: Timestamp of the creation of teh comment
    """

    post_id = db.IntegerProperty(required=True)
    username = db.StringProperty(required=True)
    comment = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
