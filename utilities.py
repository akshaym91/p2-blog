import hmac

from google.appengine.ext import db

SECRET = "nsjdvnjsvus7p2.caiud/.usdcamnsduu9w"


def securify(value):
    """Helper method to help encode the cookie data"""
    return '%s|%s' % (value, hmac.new(SECRET, value).hexdigest())


def unsecurify(secure_value):
    """Helper method to help decode the cookie data"""
    value = secure_value.split('|')[0]
    if (securify(value) == secure_value):
        return value


def blog_key(name='default'):
    return db.Key.from_path('Blog', name)
