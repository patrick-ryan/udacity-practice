import webapp2
import rot13world
import loginworld
import blogworld
import encryptworld

class MainPage(webapp2.RequestHandler):

	def get(self):
		self.response.out.write("This is the controller page.")



application = webapp2.WSGIApplication([
	('/', MainPage), 
	('/rot13', rot13world.MainPage), 
	('/simplelogin', loginworld.MainPage), 
	('/welcome', loginworld.WelcomeHandler), 
	('/blog/?(?:.json)?', blogworld.MainPage), 
	('/blog/newpost', blogworld.NewPost), 
	('/blog/(\d+)(?:.json)?', blogworld.PermalinkHandler), 
	('/blog/signup', encryptworld.Register), 
	('/blog/login', encryptworld.Login), 
	('/blog/logout', encryptworld.Logout), 
	('/victory', encryptworld.WelcomeHandler)
], debug=True)