import re
from handlers.base import Handler
from utilities import *
from classes.User import *


class SignUp(Handler):
    """
    SignUp is a class that inerits from Handler class.
    The following http methods are available on the Handler:
    get(): Displays the signup page form.
    post(): Submits the form to the database to create a new user
     and also logs the user in.
    """

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
                self.render("signup.html", errors={"username_error": message})
            else:
                user = User.register(user_username,
                                     user_password,
                                     user_email)
                user.put()
                self.login(user)
                self.redirect('/blog')


class Login(Handler):
    """
    Login is a class that inerits from Handler class.
    The following http methods are available on the Handler:
    get(): Displays the login page form.
    post(): Logs the user in and sets the appropriate calue in the cookie.
    """

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
                username_error = "User does not exist."
                self.render("login.html",
                            errors={"username_error": username_error,
                                    "password_error": password_error,
                                    "user_username": user_username,
                                    })


class Logout(Handler):
    """
    Logout is a class that inerits from Handler class.
    The following http methods are available on the Handler:
    get(): Logs the user out and resets the user_id key of the cookie.
    """

    def get(self):
        self.logout()
        self.redirect("/blog/login")
