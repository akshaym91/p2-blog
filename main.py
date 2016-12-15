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


def blog_key(name='default'):
    return db.Key.from_path('Blog', name)


class Blog(db.Model):
    """docstring for """
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class MainPage(Handler):
    """docstring for MainPage"""

    def render_front(self, subject="", content="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
        self.render("blog.html", blogs=blogs)

    def get(self):
        self.render_front()


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

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/newpost', BloggerNew),
                               ('/blog/([0-9]+)', BloggerDisplayPost)
                               ], debug=True)
