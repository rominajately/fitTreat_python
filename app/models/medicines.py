'''
Created on 18-Dec-2018

@author= Balkrishna.Meena
'''
from flask_mongoengine import Document
from mongoengine.fields import StringField
from mongoengine.fields import ListField

#  MongoDB Document for Medicine

class Medicine(Document):
    name = StringField()
    dosage = StringField()
    instructions = StringField()
    ingredients = ListField(StringField())
