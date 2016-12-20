import os
import re
import webapp2
import jinja2
import random
import string
import hashlib
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    """docstring for Handler"""

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


def blog_key(name='default'):
    return db.Key.from_path('Blog', name)


class Blog(db.Model):
    """docstring for """
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)


class MainPage(Handler):
    """docstring for MainPage"""

    def render_front(self, subject="", content="", error="", user="Anonymous"):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
        self.render("blog.html", blogs=blogs, user=user)
        # else:
        #     self.redirect('/signup')

    def get(self):
        # def make_pw_hash(name, pw, salt=""):
        #         if (salt == ""):
        #             salt = make_salt()
        #         h = hashlib.sha256(name + pw + salt).hexdigest()
        #         return '%s,%s' % (h, salt)

        # def valid_pw(name, pw, h):
        #     extracted_salt = h.split('|')[1]
        #     computed = make_pw_hash(name, pw, extracted_salt)
        #     if (computed == h):
        #         return True
        # if (valid_pw(cookie_password)):
        cookie_password = self.request.cookies.get('password')
        cookie_user = self.request.cookies.get('user')
        if (not cookie_user):
            cookie_user = "Anonymous"
        self.render_front(user=cookie_user)


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

        def make_salt():
            return ''.join(random.choice(string.letters) for x in xrange(5))

        def make_pw_hash(name, pw, salt=""):
            if (salt == ""):
                salt = make_salt()
            h = hashlib.sha256(name + pw + salt).hexdigest()
            return '%s|%s' % (h, salt)

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
            hashedpassword = make_pw_hash(user_username, user_password)
            print(hashedpassword)
            cookievalue = str('user=' + user_username +
                              '; password=' + hashedpassword + '; Path=/blog')
            self.response.headers.add_header(
                'Set-Cookie', cookievalue)
            self.redirect("/blog")


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

        def make_salt():
            return ''.join(random.choice(string.letters) for x in xrange(5))

        def make_pw_hash(name, pw, salt=""):
            if (salt == ""):
                salt = make_salt()
            h = hashlib.sha256(name + pw + salt).hexdigest()
            return '%s|%s' % (h, salt)

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
            hashedpassword = make_pw_hash(user_username, user_password)
            cookievalue = str('user=' + user_username +
                              '; password=' + hashedpassword + '; Path=/blog')
            self.response.headers.add_header(
                'Set-Cookie', cookievalue)
            self.redirect("/blog")


class BloggerNew(Handler):
    """docstring for BloggerNew"""

    def render_front(self, subject="", content="", error=""):
        self.render("newblog.html", subject=subject,
                    content=content, error=error)

    def get(self):
        self.render_front()

    def post(self):
        instance = BloggerNew()
        subject = self.request.get("subject")
        content = self.request.get("content")
        if subject and content:
            p = Blog(parent=blog_key(), subject=subject, content=content)
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
                               ('/blog/newpost', BloggerNew),
                               ('/blog/([0-9]+)', BloggerDisplayPost)
                               ], debug=True)
