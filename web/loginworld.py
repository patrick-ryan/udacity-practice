import webapp2
import re

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

def valid_user(username):
	return USER_RE.match(username)

def valid_pass(password):
	return PASS_RE.match(password)

def valid_email(email):
	if not (email):
		return True
	return EMAIL_RE.match(email)

def escape_html(text):
	for (i, o) in (("&", "&amp;"), (">", "&gt;"), ("<", "&lt;"), ('"', "&quot;")):
		text = text.replace(i, o)
	return text

form="""
<form method="post">
	<u><b>Please sign in.</b></u>
	<br>
	<br>
	<label>
		Input username: 
		<input type="text" name="username" value="%(username)s">
		<div style="color: red">%(nameerror)s</div>
	</label>
	<br>
	<label>
		Input password: 
		<input type="password" name="password" value="%(password)s">
		<div style="color: red">%(passerror)s</div>
	</label>
	<br>
	<label>
		Verify password: 
		<input type="password" name="verify" value="%(verify)s">
		<div style="color: red">%(matcherror)s</div>
	</label>
	<br>
	<label>
		Input email (optional):
		<input type="text" name="email" value="%(email)s">
		<div style="color: red">%(emailerror)s</div>
	</label>
	<br>
	<input type="submit">
</form>
"""

class MainPage(webapp2.RequestHandler):

	def write_form(self, nameerror="", passerror="", matcherror="", emailerror="", 
		username="", password="", verify="", email=""):
		self.response.out.write(form % {'nameerror': nameerror,
										'passerror': passerror,
										'matcherror': matcherror,
										'emailerror': emailerror,
										'username': escape_html(username),
										'password': escape_html(password),
										'verify': escape_html(verify),
										'email': escape_html(email)})

	def get(self):
		# self.response.headers['Content-Type'] = 'text/plain'
		self.write_form()

	def post(self):
		# self.response.headers['Content-Type'] = 'text/html'
		uusername = self.request.get("username")
		upassword = self.request.get("password")
		uverify = self.request.get("verify")
		uemail = self.request.get("email")
		USER_NAME = uusername

		username = valid_user(uusername)
		password = valid_pass(upassword)
		verify = valid_pass(uverify)
		email = valid_email(uemail)

		nameerror = ""
		passerror = ""
		matcherror = ""
		emailerror = ""

		if not username:
			nameerror = "Invalid username."
		if not password:
			passerror = "Invalid password."
		if upassword != uverify:
			matcherror = "Passwords do not match."
		if not email:
			emailerror = "Invalid email."
		if not (nameerror or passerror or matcherror or emailerror):
			self.redirect("/welcome?username=" + uusername)
		else:
			self.write_form(nameerror, passerror, matcherror, emailerror, 
				uusername, "", "", uemail)

class WelcomeHandler(webapp2.RequestHandler):

	def get(self):
		username = self.request.get("username")
		self.response.out.write("Welcome, " + username + "!")