"""
CRUD Actions of Blog-Posts
"""
from google.appengine.ext import db

from handlers.base import Handler
from utilities import *
from classes.User import *
from classes.Blog import *
from classes.Comment import *
from classes.Like import *


class AddPost(Handler):
    """
    AddPost is a class that inerits from Handler class.
    The following http methods are available on the Handler:
    get(): Displays the form with form to write a new blog.
    post(): Submits the form to a database.
    """

    def render_front(self, subject="", content="", error=""):
        if (self.get_cookie('user_id') != ''):
            user = User.by_id(int(self.get_cookie('user_id')))
            self.render("newblog.html", subject=subject,
                        content=content, error=error, user=user)
        else:
            self.redirect('/blog/login')

    def get(self):
        self.render_front()

    def post(self):
        # instance = AddPost()
        subject = self.request.get("subject")
        content = self.request.get("content")
        username = self.request.get("creator")
        if subject and content:
            p = Blog(parent=blog_key(), subject=subject,
                     content=content, username=username)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "We need both a subject and content before submitting"
            self.render_front(subject, content, error)


class EditPost(Handler):
    """
    EditPost is a class that inerits from Handler class.
    The following http methods are available on the Handler:
    get(): Displays the form with form to write a new blog.
    post(): Submits the form to a database.
    """

    def render_front(self, subject="", content="", error="", liked=False):
        if (self.get_cookie('user_id') != ''):
            user = User.by_id(int(self.get_cookie('user_id')))
            self.render("newblog.html", subject=subject,
                        content=content, error=error, user=user)
        else:
            self.redirect('/blog/login')

    def get(self, post_id):
        post_id = post_id.split('/')[0]
        key = db.Key.from_path('Blog', int(post_id), parent=blog_key())
        post = db.get(key)
        likes = Like.all().filter('post_id =', int(post_id))
        liked = False
        # if self.user:
        #     for like in likes:
        #         if self.user.name == like.username:
        #             liked = True
        #             likeId = like.key().id()
        #             break
        self.render_front(subject=post.subject,
                          content=post.content,
                          liked=liked)

    def post(self, post_id):
        post_id = post_id.split('/')[0]
        subject = self.request.get("subject")
        content = self.request.get("content")
        if subject and content:
            key = db.Key.from_path('Blog', int(post_id), parent=blog_key())
            p = db.get(key)
            p.subject = subject
            p.content = content
            p.put()
            self.redirect('/blog/%s' % post_id)
        else:
            error = "We need both a subject and content before submitting"
            self.render_front(subject, content, error)


class DisplayPost(Handler):
    """
    BloggerDisplayPost is a class that inerits from Handler class.
    The following http methods are available on the Handler:
    get(): Displays the Post in an exclusive view.
    """

    def get(self, post_id):
        """
            This renders home post page with content, comments and likes.
        """
        post_id = post_id.split('/')[0]
        key = db.Key.from_path('Blog', int(post_id), parent=blog_key())
        post = db.get(key)
        likes = Like.all().filter('post_id =', int(post_id))
        comments = Comment.all().filter('post_id =', int(post_id))
        user = User.by_id(int(self.get_cookie('user_id')))
        liked = False
        if user:
            for like in likes:
                if user.name == like.username:
                    liked = True
                    likeId = like.key().id()
                    break

        if not post:
            self.error(404)
            return

        error = self.request.get('error')

        self.render("blogpost.html", blog=post, error=error, liked=liked, comments=comments)


class DeletePost(Handler):
    """
    DeletePost is a class that inerits from Handler class.
    The following http methods are available on the Handler:
    post(): Deletes a certain post from the db.
    """

    def get(self, post_id):
        post_id = post_id.split('/')[0]
        key = db.Key.from_path('Blog', int(post_id), parent=blog_key())
        post = db.get(key)
        user = User.by_id(int(self.get_cookie('user_id')))
        if post:
            if not user:
                self.redirect('/blog/login')
            else:
                if post.username == user.name:
                    # Deleting comments before deleting post.
                    comments = Comment.all().filter('post_id =', int(post_id))
                    likes = Like.all().filter('post_id =', int(post_id))
                    for comment in comments:
                        comment.delete()
                    for like in likes:
                        like.delete()
                    post.delete()
                    return self.redirect('/blog')
                else:
                    errors = {
                        "unauth_error": "Please login to be able to delete the post."
                    }
                    self.render('error.html', errors=errors)
        else:
            errors = {
                "unauth_error": "The post you tried to delete does not exist."
            }
            self.render('error.html', errors=errors)