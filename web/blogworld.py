import os
import webapp2
import jinja2
import re
import random
import hashlib
import hmac
from string import letters
import json

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

# SUBJECT_RE = re.compile(r"^[^^]{1,2000}$")
# CONTENT_RE = re.compile(r"^[^^]{1,20000}$")

# def is_valid_subject(subject):
# 	return SUBJECT_RE.match(subject)

# def is_valid_content(content):
# 	return CONTENT_RE.match(content)

# form="""
# 		<html>
# 			<head>
# 				<title>post permalink</title>
# 			</head>
# 			<body>
# 				<div class="entity">
# 	    			<div class="entity-subject">%(subject)s</div>
# 	    			<div class="entity-content">%(content)s</div>
# 	    		</div>
# 	    	</body>
# 		<html>
# 		"""

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):

	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		return render_str(template, **params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def render_json(self, d):
		json_txt = json.dumps(d)
		self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
		self.write(json_txt)

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
		# uid = self.read_secure_cookie('user_id')
		# self.user = uid and User.by_id(int(uid))

		if self.request.url.endswith('.json'):
			self.format = 'json'
		else:
			self.format = 'html'

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Entity(db.Model):

	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

	def render(self):
		self._render_text = self.content.replace('\n', '<br>')
		return render_str("post.html", entity = self)

	def as_dict(self):
		time_fmt = '%c'
		d = {'subject': self.subject, 
			 'content': self.content, 
			 'created': self.created.strftime(time_fmt)}
		return d
	
class MainPage(Handler):

	def get(self):
		entities = Entity.all().order('-created')
		
		if self.format == 'html':
			self.render('front.html', entities = entities)
		else:
			return self.render_json([e.as_dict() for e in entities])

		# entities = db.GqlQuery("SELECT * FROM Entity "
		# 					   "ORDER BY created DESC"
		# 					   # " limit 10"
		# 					   )
		# self.render("front.html", entities=entities)
		# 
		# posts = get_posts(self.request.remote_addr)
		# self.render("front.html", posts = posts)

class NewPost(Handler):

	def render_newpost(self, subject="", content="", error=""):
		self.render("newpost.html", subject=subject, content=content, error=error)

	def get(self):
		self.render_newpost()

	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")

		# vsubject = is_valid_subject(subject)
		# vcontent = is_valid_content(content)

		if not subject or not content:
			error = "Invalid subject or blog"
			self.render_newpost(subject=subject, content=content, error=error)
		else:
			e = Entity(subject = subject, content = content)
			e.put()
			eid = str(e.key().id())

			self.redirect("/blog/" + eid)

class PermalinkHandler(Handler):

	def get(self, uri):
		key = db.Key.from_path('Entity', int(uri))
		post = db.get(key)

		if not post:
			self.error(404)
			return
		if self.format == 'html':
			self.render("permalink.html", post = post)
		else:
			self.render_json(post.as_dict())

		# e = Entity.get_by_id(int(uri))
		# subject = e.subject
		# content = e.content
		# self.response.out.write(form % {'subject': subject,
		# 								'content': content})

# class JSON(Handler):

# 	def get(self):
# 		posts = Entity.all().order('-created')

# 		self.response.headers['Content-Type'] = "application/json"
# 		self.response.out.write(json.dumps(response))