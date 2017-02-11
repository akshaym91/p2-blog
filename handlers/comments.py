"""
CRUD Actions of Comments.
"""
from google.appengine.ext import db
from datetime import datetime

from handlers.base import Handler
from utilities import *
from classes.User import *
from classes.Blog import *
from classes.Comment import *


class AddComment(Handler):
    """
    AddComment is a class that inerits from Handler class.
    The following http methods are available on the Handler:
    post(): Handles addition of a new comment for a blog post.
    """

    def post(self, post_id):
        post_id_int = int(post_id.split('/')[0])
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
                    "unauth_error": "Please login to be able to comment."
                }
                self.render('error.html', errors=errors)
            else:
                post = Blog.get_by_id(post_id_int)
                comment = self.request.get('comment')
                comment = Comment(
                    post_id=post_id_int, username=user.name, comment=comment)
                comment.put()
                self.redirect('/blog/' + post_id)


class DeleteComment(Handler):
    """
    DeleteComment is a class that inerits from Handler class.
    The following http methods are available on the Handler:
    post(): Handles deletion of a comment on the blog handler
    """

    def post(self, comment_id):
        """
        Delete the comment if the user is the commenter
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
                    "unauth_error": "Please login to delete comments"
                }
                self.render('error.html', errors=errors)
            else:
                comment = Comment.get_by_id(int(comment_id))
                if not comment:
                    errors = {
                        "unauth_error": "Comment does not exist"
                    }
                    self.render('error.html', errors=errors)
                else:
                    if comment.username == user.name:
                        comment.delete()
                        self.redirect('/blog/' + str(comment.post_id))
                    else:
                        self.redirect('/blog/comment/error')


# TODO: Fix the EditComment functionality
class EditComment(Handler):
    """
    EditComment is a class that inerits from Handler class.
    The following http methods are available on the Handler:
    post(): Handles editing of a comment on the blog handler
    """

    def get(self, comment_id):
        """
        Shows edit comment page
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
                    "unauth_error": "Please login to modify comments"
                }
                self.render('error.html', errors=errors)
            else:
                comment = Comment.get_by_id(int(comment_id))
                if not comment:
                    errors = {
                        "unauth_error": "Comment not found!"
                    }
                    self.render('error.html', errors=errors)
                else:
                    if comment.username == user.name:
                        self.render("editcomment.html", comment=comment)
                    else:
                        self.redirect('/blog/comment/error')

    def post(self, comment_id):
        """
        Actual editing of the comment with the new content.
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
                    "unauth_error": "Please login to modify comments"
                }
                self.render('error.html', errors=errors)
            else:
                comment = Comment.get_by_id(int(comment_id))
                if not comment:
                    errors = {
                        "unauth_error": "Comment not found!"
                    }
                    self.render('error.html', errors=errors)
                else:
                    if comment.username == user.name:
                        comment.comment = self.request.get('comment')
                        comment.put()
                        self.redirect('/blog/' + str(comment.post_id))
                    else:
                        self.redirect('/blog/comment/error')


class CommentError(Handler):

    def get(self):
        """
        Handles error cases when unauthorized like is requested
        """
        errors = {
            "unauth_error": "Illegal access: Cannot modify other's comments."
        }
        self.render('error.html', errors=errors)
