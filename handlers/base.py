import os
import webapp2
import jinja2

from google.appengine.ext import db

from utilities import *

from classes.User import *

template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    """
    Handler is a generic http method handling class.
    """

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
    """
    MainPage is a class that inerits from Handler class.
    The following http methods are available on the Handler:
    get(): Displays the home page with user specific information.
    """

    def render_front(self, user):
        myblogs = db.GqlQuery("SELECT * FROM Blog WHERE username = '" +
                              user.name + "' ORDER BY created DESC")
        numberofmyblogs = myblogs.count()
        blogs = db.GqlQuery("SELECT * FROM Blog WHERE username != '" +
                            user.name + "'")
        self.render("blog.html", myblogs=myblogs, blogs=blogs, user=user, numberofmyblogs=numberofmyblogs)

    def get(self):
        if self.get_cookie('user_id'):
            user = User.by_id(int(self.get_cookie('user_id')))
            if (user):
                self.render_front(user=user)
            else:
                self.redirect('/blog/signup')
        else:
            self.redirect('/blog/login')


class Home(Handler):
    """
    Home is a class that inerits from Handler class.
    The following http methods are available on the Handler:
    get(): Displays the home page with user specific information.
    """

    def get(self):
        if self.get_cookie('user_id'):
            user = User.by_id(int(self.get_cookie('user_id')))
            if (user):
                self.render_front(user=user)
            else:
                self.redirect('/blog/signup')
        else:
            self.redirect('/blog/login')