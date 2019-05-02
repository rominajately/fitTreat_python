from flask.json import JSONEncoder, JSONDecoder
from flask_mongoengine import BaseQuerySet
from app.models.user import User, Messages
from app.models.meal import Meal
from app.models.medicines import Medicine
from app.models.symptoms import Symptom
from app.models.appData import AppData

# Converts Python Objects to JSON Objects
# All the data bindings in Android Application is through JSON therefore conversion is necessary

from mongoengine import DoesNotExist

class Encoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, AppData):
            return {
                '_id': str(obj.id),
                'aboutSection': obj.aboutSection,
                'references': obj.references
            }
        elif isinstance(obj, User):
            return {
                '_id' : str(obj.id),
                'email': obj.email,
                'firstName': obj.firstName,
                'lastName': obj.lastName,
                'gender': obj.gender,
                # 'password': obj.password,
                'resetPasswordToken': obj.resetPasswordToken,
                'resetPasswordExpires': obj.resetPasswordExpires,
                'role': obj.role,
                'dateOfBirth': obj.dateOfBirth,
                'age': obj.age,
                'weight': obj.weight,
                'weightUnit': obj.weightUnit,
                'height': float(obj.height),
                'heightUnit': obj.heightUnit,
                'foodPreference': obj.foodPreference,
                'timeZone': obj.timeZone,
                'bmi': obj.bmi,
                'medicalCondition': obj.medicalCondition,
                'targetWeight': obj.targetWeight,
                'targetDate': obj.targetDate,
                'targetCalories': obj.targetCalories,
                'accountCreationDate': obj.accountCreationDate,
                'userPhoto': obj.userPhoto,
                'messages': [msg for msg in obj.messages],
                'mealAssigned': populate(modelName='Meal', docs=obj.mealAssigned),
                'mealExpiry': obj.mealExpiry,
                'unreadCount':obj.unreadCount
            }
        elif isinstance(obj,Messages):
            return {
                '_id':str(obj._id),
                'subject':obj.subject,
                'content':obj.content,
                'createDate':obj.createDate,
                'readFlag':obj.readFlag
            }
        elif isinstance(obj, Meal):
            return {
                '_id':str(obj.id),
                'name': obj.name,
                'foodPreference': obj.foodPreference,
                'cuisine': obj.cuisine,
                'dietType': [d for d in obj.dietType],
                'idealMedCond': [imc for imc in obj.idealMedCond],
                'avoidableMedCond': [amc for amc in obj.avoidableMedCond],
                'course': obj.course,
                'calories': obj.calories,
                'nutritionInfo': obj.nutritionInfo,
                'ingredients': obj.ingredients,
                'directions': obj.directions,
                'photoURL': obj.photoURL,
                'servingSize':obj.servingSize
            }
        elif isinstance(obj, Medicine):
            return {
                '_id': str(obj.id),
                'name': obj.name,
                'dosage': obj.dosage,
                'instructions': obj.instructions,
                'ingredients': [ing for ing in obj.ingredients]
            }
        elif isinstance(obj, Symptom):
            return {
                '_id': str(obj.id),
                'name': obj.name,
                'indications': obj.indications,
                'medicines': populate(modelName='Medicine', docs=obj.medicines)
            }
        elif isinstance(obj, BaseQuerySet):
            ret = []
            for o in obj:
                ret.append(self.default(o))
            return ret
        return super(Encoder, self).default(obj)


class Decoder(JSONDecoder):
    def default(self, obj):
        #print(type(obj))
        if isinstance(obj, User):
            return {
                'email': obj.email,
                'firstName': obj.firstName,
                'lastName': obj.lastName
            }
        elif isinstance(obj, Meal):
            pass
        elif isinstance(obj, Medicine):
            pass
        elif isinstance(obj, Symptom):
            pass
        elif isinstance(obj, BaseQuerySet):
            ret = []
            for o in obj:
                ret.append(self.default(o))
            return ret
        return super(Decoder, self).default(obj)


def populate(modelName, docs):
    ret = []
    for doc in docs:
        try:
            ret.append(globals()[modelName].objects(id = doc.id).get())
        except DoesNotExist:
            pass

    return ret
