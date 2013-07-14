import os
import webapp2
import jinja2
import re
import random
import hashlib
import hmac
from string import letters

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
	autoescape = True)

secret = 'randomletters'

def make_secure_val(val):
	return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
	val = secure_val.split('|')[0]
	if secure_val == make_secure_val(val):
		return val

class Handler(webapp2.RequestHandler):

	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def set_secure_cookie(self, name, val):
		cookie_val = make_secure_val(val)
		self.response.headers.add_header(
			'Set-Cookie', 
			'%s=%s; Path=/' % (name, cookie_val))

	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and check_secure_val(cookie_val)

	def login(self, user):
		self.set_secure_cookie('user_id', str(user.key().id()))

	def logout(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie('user_id')
		self.user = uid and User.by_id(int(uid))

		if self.request.url.endswith('.json'):
			self.format = 'json'
		else:
			self.format = 'html'

def make_salt(length = 5):
	return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	hash_val = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s,%s' % (salt, hash_val)

def valid_pw(name, password, hash_val):
	salt = hash_val.split(',')[0]
	return hash_val == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
	return db.Key.from_path('users', group)

class User(db.Model):

	username = db.StringProperty(required = True)
	pw_hash = db.StringProperty(required = True)
	email = db.StringProperty()

	@classmethod
	def by_id(cls, uid):
		return User.get_by_id(uid, parent = users_key())

	@classmethod
	def by_name(cls, username):
		u = User.all().filter('username =', username).get()
		return u

	@classmethod
	def register(cls, username, pw, email = None):
		pw_hash = make_pw_hash(username, pw)
		return User(parent = users_key(), 
					username = username, 
					pw_hash = pw_hash, 
					email = email)

	@classmethod
	def login(cls, username, pw):
		u = cls.by_name(username)
		if u and valid_pw(username, pw, u.pw_hash):
			return u

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

def valid_user(username):
	return USER_RE.match(username)

def valid_pass(password):
	return PASS_RE.match(password)

def valid_email(email):
	if not email:
		return True
	return EMAIL_RE.match(email)

class MainPage(Handler):

	def get(self):
		self.render('signup.html')

	def post(self):
		have_error = False
		self.username = self.request.get("username")
		self.password = self.request.get("password")
		self.verify = self.request.get("verify")
		self.email = self.request.get("email")

		params = dict(username = self.username, email = self.email)

		if not valid_user(self.username):
			params['nameerror'] = "Invalid username."
			have_error = True
		if not valid_pass(self.password):
			params['passerror'] = "Invalid password."
			have_error = True
		if self.password != self.verify:
			params['matcherror'] = "Passwords do not match."
			have_error = True
		if not valid_email(self.email):
			params['emailerror'] = "Invalid email."
			have_error = True
		if have_error:
			self.render('signup.html', **params)
		else:
			self.done()

	def done(self, *a, **kw):
		raise NotImplementedError

class Register(MainPage):

	def done(self):
		u = User.by_name(self.username)
		if u:
			msg = 'That user already exists.'
			self.render('signup.html', existserror = msg)
		else:
			u = User.register(self.username, self.password, self.email)
			u.put()
			self.login(u)
			self.redirect('/victory')

class Login(Handler):

	def get(self):
		self.render('login-form.html')

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		u = User.login(username, password)
		if u:
			self.login(u)
			self.redirect('/victory')
		else:
			msg = 'Invalid login.'
			self.render('login-form.html', error = msg)

class Logout(Handler):

	def get(self):
		self.logout()
		self.redirect('/signup')

class WelcomeHandler(Handler):

	def get(self):
		if self.user:
			username = self.user.username
			self.response.out.write("Welcome, " + username + "!")
			# self.render('welcome.html', username = self.user.username)
		else:
			self.redirect('/signup')