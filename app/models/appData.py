'''
Created on 18-Dec-2018

'''
from flask_mongoengine import Document
from mongoengine.fields import StringField

# MongoDB Document for Application Data (About, References)
#  Used in Admin Panel

class AppData(Document):
    aboutSection = StringField(default='This is a test html text.')
    references = StringField(default='This is a test reference text.')
