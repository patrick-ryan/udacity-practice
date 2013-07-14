import webapp2

def encrypt(text):
	return text.encode("rot13")

def escape_html(text):
	for (i, o) in (("&", "&amp;"), (">", "&gt;"), ("<", "&lt;"), ('"', "&quot;")):
		text = text.replace(i, o)
	return text

form="""
<form method="post">
	This is my ROT13 web-app.
	<br>
	<textarea name="text" rows="4" cols="50">%(entry)s</textarea>
	<br>
	<input type="submit">
</form>
"""

class MainPage(webapp2.RequestHandler):

	def write_form(self, entry=""):
		self.response.out.write(form % {'entry': escape_html(entry)})

	def get(self):
		# self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write(form)

	def post(self):
		# self.response.headers['Content-Type'] = 'text/html'
		user_entry = self.request.get("text")
		new_entry = encrypt(user_entry)
		self.write_form(new_entry)


# class TestHandler(webapp2.RequestHandler):

# 	def post(self):
# 		q = self.request.get("q")
# 		self.response.out.write(q)

# 		self.response.headers['Content-Type'] = 'text/plain'
# 		self.response.out.write(self.request)