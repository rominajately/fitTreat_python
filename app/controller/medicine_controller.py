from flask import request
from flask.json import jsonify

from attrdict import AttrDict
from mongoengine import NotUniqueError

from app.models.medicines import Medicine
from flask_api import status

''' 
Context - App Administration
API to add medicines to the database
'''

def addMedicines():
    data = request.get_json()
    meds = Medicine.objects.insert([Medicine(name=med['name'], dosage=med['dosage'] if 'dosage' in med else None,
                                             instructions=med['instructions'] if 'instructions' in med else None,
                                             ingredients=[ing for ing in med['ingredients']]) for med in data])
    return jsonify(meds), status.HTTP_200_OK

''' 
Context - App Administration
API to get all the medicines in the database 
'''
def getAllMedicines():
    return jsonify(Medicine.objects), status.HTTP_200_OK

''' 
Context - App Administration
API to delete all the medicines from the DB 
'''

def deleteMeds():
    idArr = request.get_json()
    try:
        delMeds = Medicine.objects(id__in=idArr)
        if delMeds:
            delMeds = delMeds.delete()
            return jsonify({'stat': 'Success'}),status.HTTP_200_OK
        else:
            return jsonify({'stat': 'Medicines not deleted'}), status.HTTP_500_INTERNAL_SERVER_ERROR
    except Exception as e:
        return jsonify({'Error': format(e)}), status.HTTP_404_NOT_FOUND

''' 
Context - App Administration
API to add new medicine
'''
def addNewMedicine():
    data = AttrDict(request.get_json())
    try:
        newMed = Medicine(name=data.name, dosage=data.dosage, \
                          instructions=data.instructions, ingredients=[ing for ing in data.ingredients]).save()
        return jsonify(newMed), status.HTTP_200_OK
    except NotUniqueError:
        return jsonify({'stat': 'Medicine already exists.'}), status.HTTP_200_OK
    except Exception as e:
        return jsonify({'Error': format(e)}), status.HTTP_400_BAD_REQUEST
