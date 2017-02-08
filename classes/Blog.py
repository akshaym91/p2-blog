from google.appengine.ext import db


class Blog(db.Model):
    """
    Blog is a model class which has the following attributes
    subject: Title of the blog post
    content: Content of the blog
    created: The timestamp for the blog post creation time
    last_modified: Timestamp that indicates the last modification
    username: name of the author of the blog post
    comments: Number of comments that the blog post has
    likes: Number of likes the blog post has
    """

    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    username = db.StringProperty(required=True)
    comments = db.IntegerProperty()
    likes = db.IntegerProperty()
