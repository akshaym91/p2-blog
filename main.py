import webapp2

from classes.User import *
from classes.Blog import *
from classes.Comment import *
from classes.Like import *

from handlers.base import Handler, MainPage, Home
from handlers.authentication import SignUp, Login, Logout
from handlers.posts import AddPost, EditPost, DisplayPost, DeletePost
from handlers.likes import LikePost, UnlikePost, LikeError
from handlers.comments import AddComment, EditComment, DeleteComment, CommentError

app = webapp2.WSGIApplication([
    ('/', Home),
    ('/blog', MainPage),
    ('/blog/signup', SignUp),
    ('/blog/login', Login),
    ('/blog/logout', Logout),
    ('/blog/newpost', AddPost),
    ('/blog/([0-9]+)', DisplayPost),
    ('/blog/([0-9]+/edit)', EditPost),
    ('/blog/([0-9]+)/delete', DeletePost),
    ('/blog/([0-9]+)/like', LikePost),
    ('/blog/([0-9]+)/unlike', UnlikePost),
    ('/blog/like/error', LikeError),
    ('/blog/([0-9]+)/addComment', AddComment),
    ('/blog/([0-9]+)/editComment', EditComment),
    ('/blog/([0-9]+)/deleteComment', DeleteComment),
    ('/blog/comment/error', CommentError),
], debug=True)
