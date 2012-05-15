"""
Frontend for the image host. This does the actual serving of the images
for use on others sites and within the admin
"""

import os
import datetime
import webapp2

from google.appengine.ext import db

from models import Image
  
class GenericServer(webapp2.RequestHandler):
    """
    Image server designed to handle serving png images from
    different object properties
    """
    property = 'image'
    def get(self):
        # key is provided in the query string
        img = self.request.get("id")
        try:
            # it might be an invalid key so we better check
            image = Image.get_by_key_name_or_id(img)
        except db.BadKeyError:
            # if it is then return a 404
            self.error(404)
            return
            
        if image and image.image:
            # we have an image so prepare the response
            # with the relevant headers
            self.response.headers['Content-Type'] = "image/png"
            # and then write our the image data direct to the response
            self.response.out.write(eval("image.%s" % self.property))
        else:
            # we should probably return an image with the correct header
            # here instead of the default html 404
            self.error(404)

class ImageServer(GenericServer):
    "Serve the main image"
    property = 'image'

class ThumbServer(GenericServer):
    "Serve the thumbnail image"
    property = 'thumb'

class OriginalServer(GenericServer):
    "Serve the original uploaded image. Currently unused."
    property = 'original'

app = webapp2.WSGIApplication([
    ('/i/img', ImageServer),
    ('/i/thumb', ThumbServer),
], debug=True)
