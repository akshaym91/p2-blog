import os
import webapp2
import jinja2
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


class Blog(db.Model):
    """docstring for """
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    id = db.IntegerProperty()


class MainPage(Handler):
    """docstring for MainPage"""

    def render_front(self, title="", content="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
        self.render("blog.html", blogs=blogs)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")
        id = STATIC_ID_GEN + 1
        STATIC_ID_GEN = STATIC_ID_GEN + 1
        if title and content:
            a = Blog(title=title, content=content, id=id)
            a.put()
            self.redirect("/blog/{{blog.id}}")
        else:
            error = "We need both a title and content before submitting"
            self.render_front(title, content, error)


class BloggerNew(Handler):
    """docstring for BloggerNew"""

    STATIC_ID_GEN = 0

    def render_front(self, title="", content="", error=""):
        self.render("newblog.html", title=title,
                    content=content, error=error)

    def get(self):
        self.render_front()

    def post(self):
        instance = BloggerNew()
        title = self.request.get("title")
        content = self.request.get("content")
        id = instance.STATIC_ID_GEN + 1
        instance.STATIC_ID_GEN = instance.STATIC_ID_GEN + 1
        if title and content:
            a = Blog(title=title, content=content, id=id)
            a.put()
            self.redirect('/blog/%s' % id)
        else:
            error = "We need both a title and content before submitting"
            self.render_front(title, content, error)


class BloggerDisplayPost(Handler):
    """docstring for DisplayPost"""

    def get(self, post_id):
        blog = Blog(db.GqlQuery("SELECT * FROM Blog WHERE id=" + post_id))
        self.render("blogpost.html", blog=blog)


class ThanksHandler(Handler):
    """docstring for ThanksHandler"""

    def get(self):
        user_username = self.request.get('user_username')
        self.render("thanks.html", user_username=user_username)

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/newpost', BloggerNew),
                               (r'/blog/(\d+)>', BloggerDisplayPost),
                               ('/thanks', ThanksHandler)], debug=True)
