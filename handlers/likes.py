"""
CRUD Actions of Likes.
"""
from google.appengine.ext import db
from datetime import datetime

from handlers.base import Handler
from utilities import *
from classes.User import *
from classes.Blog import *
from classes.Like import *


class LikePost(Handler):
    """
    LikePost is a class that inerits from Handler class.
    The following http methods are available on the Handler:
    post(): Handles like action on a blog post.
    """

    def get(self, post_id):
        """
        Like a post created by self
        """
        user_cookie = self.get_cookie('user_id')
        if not user_cookie:
            errors = {
                "unauth_error": "Login error or Session timeout"
            }
            self.render('error.html', errors=errors)
        else:
            user = User.by_id(int(user_cookie))
            if not user:
                errors = {
                    "unauth_error": "Please login to be able to like."
                }
                self.render('error.html', errors=errors)
            else:
                post_id_int = int(post_id.split('/')[0])
                post = Blog.by_id(post_id_int)
                author = post.username
                if author == user.name or Like.all().filter('post_id =', post_id_int).filter('username =', user.name).get() != None:
                    self.redirect('/blog/like/error')
                else:
                    like = Like(post_id=post_id_int, username=user.name)
                    like.put()
                    self.redirect('/blog/' + post_id)


class UnlikePost(Handler):
    """
    UnlikePost is a class that inerits from Handler class.
    The following http methods are available on the Handler:
    post(): Handles unlike action on a blog post.
    """

    def get(self, post_id):
        """
        Unlike a post not created by self
        """
        user_cookie = self.get_cookie('user_id')
        if not user_cookie:
            errors = {
                "unauth_error": "Login error or Session timeout"
            }
            self.render('error.html', errors=errors)
        else:
            user = User.by_id(int(user_cookie))
            if not user:
                errors = {
                    "unauth_error": "Please login to be able to unlike."
                }
                self.render('error.html', errors=errors)
            else:
                post_id_int = int(post_id.split('/')[0])
                post = Blog.by_id(post_id_int)
                author = post.username
                if author == user.name or Like.all().filter('post_id =', post_id_int).filter('username =', user.name).get() != None:
                    self.redirect('/blog/like/error')
                else:
                    like = Like.by_name(user.name)
                    if not like:
                        self.redirect('/blog/unlike/error')
                    else:
                        like.delete()
                        self.redirect('/blog/' + post_id)


class LikeError(Handler):

    def get(self):
        """
        Handles error cases when unauthorized like is requested
        """
        errors = {
            "unauth_error": "You can't like your own post & can only like a post once."
        }
        self.render('error.html', errors=errors)

class UnlikeError(Handler):

    def get(self):
        """
        Handles error cases when unauthorized like is requested
        """
        errors = {
            "unauth_error": "You can't unlike your own post & can only like a post once."
        }
        self.render('error.html', errors=errors)
