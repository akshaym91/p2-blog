import os
import sys
import re
import webapp2
import jinja2
import random
import string
import hashlib
import hmac
from google.appengine.ext import db

# sys.path.append('./classes')

# from User import *
# from Blog import *

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

SECRET = "nsjdvnjsvus7p2.caiud/.usdcamnsduu9w"


def securify(value):
    return '%s|%s' % (value, hmac.new(SECRET, value).hexdigest())


def unsecurify(secure_value):
    value = secure_value.split('|')[0]
    if (securify(value) == secure_value):
        return value


def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))


def make_pw_hash(name, pw, salt=""):
    if (salt == ""):
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s|%s' % (h, salt)


def valid_pw(name, pw, h):
    extracted_salt = h.split('|')[1]
    computed = make_pw_hash(name, pw, extracted_salt)
    if (computed == h):
        return True


def blog_key(name='default'):
    return db.Key.from_path('Blog', name)


def user_key(name='default'):
    return db.Key.from_path('User', name)


class Handler(webapp2.RequestHandler):
    """docstring for Handler"""

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_cookie(self, name, value):
        cookie_value = securify(value)
        self.response.headers.add_header(
            'Set-Cookie', '%s=%s; Path=/blog' % (name, cookie_value))

    def get_cookie(self, name):
        cookie_value = self.request.cookies.get(name)
        return cookie_value and unsecurify(cookie_value)

    def login(self, user):
        self.set_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header(
            'Set-Cookie', 'user_id=; Path=/blog')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.get_cookie('user_id')
        return uid and User.by_id(int(uid))


class MainPage(Handler):
    """docstring for MainPage"""

    def render_front(self, user):
        myblogs = db.GqlQuery("SELECT * FROM Blog WHERE creator_id = '" +
                              user.name + "' ORDER BY created DESC")
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
        self.render("blog.html", myblogs=myblogs, blogs=blogs, user=user)

    def get(self):
        if self.get_cookie('user_id'):
            user = User.by_id(int(self.get_cookie('user_id')))
            if (user):
                self.render_front(user=user)
            else:
                self.redirect('/blog/signup')
        else:
            self.redirect('/blog/login')


class User(db.Model):
    """docstring for User"""

    name = db.StringProperty(required=True)
    hashed_password = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent=user_key())

    @classmethod
    def by_name(cls, name):
        return User.all().filter("name =", name).get()

    @classmethod
    def register(cls, name, password, email=None):
        hashed_password = make_pw_hash(name, password)
        return User(parent=user_key(),
                    name=name,
                    hashed_password=hashed_password,
                    email=email)

    @classmethod
    def retrieve(cls, name, password):
        user = User.by_name(name)
        if user and valid_pw(name, password, user.hashed_password):
            return user


class Blog(db.Model):
    """docstring for Blog"""
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    creator_id = db.StringProperty(required=True)


class SignUp(Handler):
    """docstring for SignUp"""

    def get(self):
        errors = {"username_error": "",
                  "password_error": "",
                  "verify_error": "",
                  "email_error": "",
                  "user_username": "",
                  "user_email": ""}
        self.render("signup.html", errors=errors)

    def post(self):

        def validate_username(username):
            USERNAME_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
            return USERNAME_RE.match(username)

        def validate_email(email):
            EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
            if(EMAIL_RE.match(email) or email == ""):
                return True
            return EMAIL_RE.match(email)

        def validate_password(password):
            PASSWORD_RE = re.compile(r"^.{3,20}$")
            return PASSWORD_RE.match(password)

        user_username = self.request.get('username')
        user_password = self.request.get('password')
        user_verifypassword = self.request.get('verify')
        user_email = self.request.get('email')

        test_username = validate_username(user_username)
        test_password = (validate_password(user_password) and
                         (user_password == user_verifypassword))
        test_email = validate_email(user_email)
        username_error = ""
        password_error = ""
        verify_error = ""
        email_error = ""
        if (not test_username):
            username_error = "Invalid Username."

        if (not validate_password(user_password)):
            password_error = "Invalid Password."

        if (not (user_password == user_verifypassword)):
            verify_error = "Password mismatch."

        if (not test_email):
            email_error = "Invalid Email."

        if not (test_username and
                test_password and
                test_email and
                (user_password == user_verifypassword)):
            self.render("signup.html",
                        errors={"username_error": username_error,
                                "password_error": password_error,
                                "verify_error": verify_error,
                                "email_error": email_error,
                                "user_username": user_username,
                                "user_email": user_email})
        else:
            user = User.by_name(user_username)
            if user:
                message = 'That user already exists'
                self.render("signup.html", username_error=message)
            else:
                user = User.register(user_username,
                                     user_password,
                                     user_email)
                user.put()
                self.login(user)
                self.redirect('/blog')


class Login(Handler):
    """docstring for Login"""

    def get(self):
        errors = {"username_error": "",
                  "password_error": ""}
        self.render("login.html", errors=errors)

    def post(self):

        def validate_username(username):
            USERNAME_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
            return USERNAME_RE.match(username)

        def validate_password(password):
            PASSWORD_RE = re.compile(r"^.{3,20}$")
            return PASSWORD_RE.match(password)

        user_username = self.request.get('username')
        user_password = self.request.get('password')

        test_username = validate_username(user_username)
        test_password = validate_password(user_password)

        username_error = ""
        password_error = ""

        if (not test_username):
            username_error = "Invalid Username."

        if (not validate_password(user_password)):
            password_error = "Invalid Password."

        if not (test_username and test_password):
            self.render("login.html",
                        errors={"username_error": username_error,
                                "password_error": password_error,
                                "user_username": user_username,
                                })
        else:
            user = User.retrieve(user_username, user_password)
            if user:
                self.login(user)
                self.redirect('/blog')
            else:
                username_error = "User already exists"
                self.render("login.html",
                            errors={"username_error": username_error,
                                    "password_error": password_error,
                                    "user_username": user_username,
                                    })


class Logout(Handler):
    """docstring for Logout"""

    def get(self):
        self.logout()
        self.redirect("/blog/login")


class BloggerNew(Handler):
    """docstring for BloggerNew"""

    def render_front(self, subject="", content="", error=""):
        user = User.by_id(int(self.get_cookie('user_id')))
        self.render("newblog.html", subject=subject,
                    content=content, error=error, user=user)

    def get(self):
        self.render_front()

    def post(self):
        # instance = BloggerNew()
        subject = self.request.get("subject")
        content = self.request.get("content")
        creator_id = self.request.get("creator")
        if subject and content:
            p = Blog(parent=blog_key(), subject=subject,
                     content=content, creator_id=creator_id)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "We need both a subject and content before submitting"
            self.render_front(subject, content, error)


class BloggerDisplayPost(Handler):
    """docstring for DisplayPost"""

    def get(self, post_id):
        """
            This renders home post page with content, comments and likes.
        """
        key = db.Key.from_path('Blog', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        error = self.request.get('error')

        self.render("blogpost.html", blog=post, error=error)

app = webapp2.WSGIApplication([('/blog', MainPage),
                               ('/blog/signup', SignUp),
                               ('/blog/login', Login),
                               ('/blog/logout', Logout),
                               ('/blog/newpost', BloggerNew),
                               ('/blog/([0-9]+)', BloggerDisplayPost)
                               ], debug=True)
