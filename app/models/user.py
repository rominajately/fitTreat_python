'''
Created on 18-Dec-2018

@author: Balkrishna.Meena
'''
from datetime import datetime
from app import bcrypt
from mongoengine.signals import pre_save
from dateutil import parser, relativedelta
from bson import ObjectId
from mongoengine.fields import ListField
from flask_mongoengine import Document
from mongoengine.base.fields import BaseField, ObjectIdField
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField, EmailField, DateTimeField, IntField, \
    EmbeddedDocumentField, ReferenceField, BooleanField, DecimalField,BinaryField

from app.models.meal import Meal

#  MongoDB Document for Messages

class Messages(EmbeddedDocument):
    subject = StringField()
    createDate = DateTimeField(default=datetime.utcnow())
    readFlag = BooleanField(default=False)
    content = StringField()
    _id = ObjectIdField(default=ObjectId)

#  MongoDB Document for User

class User(Document):
    firstName = StringField(required=True)
    lastName = StringField(required=True, default='')
    email = EmailField(required=True)
    gender = StringField(required=True, default='Male')  # choices=['Male', 'Female', 'Other'])
    password = BinaryField()
    resetPasswordToken = StringField()
    resetPasswordExpires = DateTimeField()
    role = StringField(default='User')  # choices=['User', 'Admin'])
    dateOfBirth = StringField(required=True)  # YYYY/MM/DD Format
    age = IntField(required=True, default=0)
    weight = IntField(required=True, default=0)
    weightUnit = StringField(required=True, default='kg')  # choices=['kg', 'lb'])
    height = DecimalField(required=True, default=0, precision=1)
    heightUnit = StringField(required=True, default='cm')  # choices=['cm', 'm', 'ft'])
    foodPreference = StringField(required=True,
                                 default='Vegetarian')  # choices=['Vegan', 'Vegetarian', 'Non-Vegetarian'])
    timeZone = StringField(default='0')  # Timezone Offset Value
    bmi = IntField(default=0)
    medicalCondition = StringField()
    targetWeight = IntField(default=0)
    targetDate = StringField(default='')  # YYYY/MM/DD format
    targetCalories = IntField(default=0)
    accountCreationDate = DateTimeField(default=datetime.utcnow())
    userPhoto = StringField(default='')
    messages = ListField(EmbeddedDocumentField(Messages))
    mealAssigned = ListField(ReferenceField(Meal))
    mealExpiry = DateTimeField()
    unreadCount = IntField(default=0)

    @staticmethod
    def pre_save_func(sender, document):
        document['password'] = bcrypt.generate_password_hash(document['password'])
        dob = parser.parse(document['dateOfBirth'])
        today = datetime.today()
        age = relativedelta.relativedelta(today, dob)
        document['age'] = age.years


pre_save.connect(User.pre_save_func, sender=User)
