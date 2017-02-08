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
        user = User.by_id(int(self.get_cookie('user_id')))
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
            # Comments counter
            # Default value is None
            # If post has not comments, set it to one
            # if post.comments is None:
            #     post.comments = 1
            # else:
            #     post.comments = int(post.comments) + 1
            # Update comments count
            # post.put()
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
        user = User.by_id(int(self.get_cookie('user_id')))
        comment = Comment.get_by_id(int(comment_id))
        if not user:
            errors = {
                "unauth_error": "Please login to be able to comment."
            }
            self.render('error.html', errors=errors)
        else:
            if comment.username == user.name:
                comment.delete()
                self.redirect('/blog/' + post_id)
            else:
                self.redirect('/comment/error')


# TODO: Fix the EditComment functionality
class EditComment(Handler):
    """
    EditComment is a class that inerits from Handler class.
    The following http methods are available on the Handler:
    post(): Handles editing of a comment on the blog handler
    """

    def post(self, post_id):
        post_id = post_id.split('/')[0]
        key = db.Key.from_path('Blog', int(post_id), parent=blog_key())
        post = db.get(key)
        if post:
            commentId = self.request.get('commentId')
            editComment = self.request.get('editComment')
            if commentId and editComment and self.user:
                key = db.Key.from_path('Comment', int(
                    commentId), parent=blog_key())
                comment = db.get(key)
                if comment:
                    if comment.username == self.user.name:
                        comment.comment = editComment
                        comment.put()
                        return self.redirect('/blog/' + post_id)
                else:
                    return self.redirect('/blog/' + post_id)
            else:
                return self.redirect('/')
        else:
            return self.redirect('/')


class CommentError(Handler):

    def get(self):
        """
        Handles error cases when unauthorized like is requested
        """
        errors = {
            "unauth_error": "You can't comment your own post & can only like a post once."
        }
        self.render('error.html', errors=errors)
