"""
Provides a protected administrative area for uploading and deleteing images
"""

import datetime
import jinja2
import os
import webapp2

from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import users

from models import Image

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(
    os.path.join(os.path.dirname(__file__), 'templates')))

class Index(webapp2.RequestHandler):
    """
    Main view for the application.
    Protected to logged in users only.
    """
    def get(self):
        "Responds to GET requets with the admin interface"
        images = Image.all()
        images.order("-date")

        # we need the logout url for the frontend
        logout = users.create_logout_url("/")

        # prepare the context for the template
        context = {
            "images": images,
            "logout": logout,
        }
        template = jinja_environment.get_template('index.html')
        # render the template with the provided context
        self.response.out.write(template.render(context))

class Deleter(webapp2.RequestHandler):
    "Deals with deleting images"
    def post(self):
        "Delete a given image"
        key = self.request.get("key")
        if key:
            image = Image.get_by_key_name_or_id(key)
            image.delete()
        # whatever happens rediect back to the main admin view
        self.redirect('/')
       
class Uploader(webapp2.RequestHandler):
    "Deals with uploading new images to the datastore"
    def post(self):
        "Upload via a multitype POST message"
        
        img = self.request.get("img")

        # if we don't have image data we'll quit now
        if not img:
            self.redirect('/')
            return 
            
        # we have image data
        try:
            # check we have numerical width and height values
            width = int(self.request.get("width"))
            height = int(self.request.get("height"))
        except ValueError:
            # if we don't have valid width and height values
            # then just use the original image
            image_content = img
        else:
            # if we have valid width and height values
            # then resize according to those values
            image_content = images.resize(img, width, height)
        
        # always generate a thumbnail for use on the admin page
        thumb_content = images.resize(img, 100, 100)
        
        # create the image object
        if self.request.get("name"):
            image = Image(key_name=self.request.get("name"))
        else:
            image = Image()
        # and set the properties to the relevant values
        image.image = db.Blob(image_content)
        image.thumb = db.Blob(thumb_content)
        image.user = users.get_current_user()
                
        # store the image in the datasore
        image.put()
        # and redirect back to the admin page
        self.redirect('/')
                
# wire up the views
app = webapp2.WSGIApplication([
    ('/', Index),
    ('/upload', Uploader),
    ('/delete', Deleter)
], debug=True)
