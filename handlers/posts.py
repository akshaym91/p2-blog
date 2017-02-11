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
        user = User.by_id(int(self.get_cookie('user_id')))
        if not user:
            self.redirect('/blog/login')
        else:
            self.render("newblog.html", subject=subject,
                        content=content, error=error, user=user)

    def get(self):
        self.render_front()

    def post(self):
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
                    "unauth_error": "Please login to be able to add posts"
                }
                self.render('error.html', errors=errors)
            else:
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
        user = User.by_id(int(self.get_cookie('user_id')))
        if not user:
            self.redirect('/blog/login')
        else:
            self.render("newblog.html", subject=subject,
                        content=content, error=error, user=user)

    def get(self, post_id):
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
                    "unauth_error": "Please login to be able to edit posts"
                }
                self.render('error.html', errors=errors)
            else:
                post_id_int = int(post_id.split('/')[0])
                post = Blog.by_id(post_id_int)
                if not post:
                    errors = {
                        "unauth_error": "This Blog post is missing"
                    }
                    self.render('error.html', errors=errors)
                else:
                    if post.username == user.name:
                        key = db.Key.from_path(
                            'Blog', post_id_int, parent=blog_key())
                        post = db.get(key)
                        liked = False
                        self.render_front(subject=post.subject,
                                          content=post.content,
                                          liked=liked)
                    else:
                        errors = {
                            "unauth_error": "You can modify self-written posts only"
                        }
                        self.render('error.html', errors=errors)

    def post(self, post_id):
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
                    "unauth_error": "Please login to be able to edit posts"
                }
                self.render('error.html', errors=errors)
            else:
                post_id_int = int(post_id.split('/')[0])
                post = Blog.by_id(post_id_int)
                if not post:
                    errors = {
                        "unauth_error": "This Blog post is missing"
                    }
                    self.render('error.html', errors=errors)
                else:
                    if post.username == user.name:
                        subject = self.request.get("subject")
                        content = self.request.get("content")
                        if subject and content:
                            post.subject = subject
                            post.content = content
                            post.put()
                            self.redirect('/blog/' + str(post_id_int))
                        else:
                            error = "We need both a subject and content before submitting"
                            self.render_front(subject, content, error)
                    else:
                        errors = {
                            "unauth_error": "You can modify self-written posts only"
                        }
                        self.render('error.html', errors=errors)


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
        user_cookie = self.get_cookie('user_id')
        if not user_cookie:
            errors = {
                "unauth_error": "Login error or Session timeout"
            }
            self.render('error.html', errors=errors)
        else:
            user = User.by_id(int(user_cookie))
            liked = False

            if not post:
                errors = {
                    "unauth_error": "This Blog post is missing"
                }
                self.render('error.html', errors=errors)
            else:
                if not user:
                    errors = {
                        "unauth_error": "Please login to be able to edit posts"
                    }
                    self.render('error.html', errors=errors)
                else:
                    for like in likes:
                        if user.name == like.username:
                            liked = True
                            likeId = like.key().id()
                            break
                    error = self.request.get('error')
                    self.render("blogpost.html", blog=post, error=error,
                                liked=liked, comments=comments, user=user)


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
        user_cookie = self.get_cookie('user_id')
        if not user_cookie:
            errors = {
                "unauth_error": "Login error or Session timeout"
            }
            self.render('error.html', errors=errors)
        else:
            user = User.by_id(int(user_cookie))
            if post:
                if not user:
                    errors = {
                        "unauth_error": "Please login to be able to edit posts."
                    }
                    self.render('error.html', errors=errors)
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
                            "unauth_error": "You can delete self-written posts only"
                        }
                        self.render('error.html', errors=errors)
            else:
                errors = {
                    "unauth_error": "The post you tried to delete does not exist."
                }
                self.render('error.html', errors=errors)
