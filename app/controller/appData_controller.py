import json

from flask import request
from flask.json import jsonify

from attrdict import AttrDict
from mongoengine import DoesNotExist
from flask_api import status

from app.models.appData import AppData

''' Used to set Application Data '''
def setAppDefaultData(id):
    data = AttrDict(request.get_json())
    try:
        ad = AppData.objects(id=id).update_one(aboutSection=data.aboutSection, references=data.references)
        print('printing ad')
        return jsonify({'status': 'success'}), status.HTTP_200_OK
    except Exception as e:
        print('Error while saving app data', e)
        return jsonify({'Error': format(e)}), status.HTTP_400_BAD_REQUEST

''' Used to serve Application Data to requesting source'''
def getAppDefaultData():
    return jsonify(AppData.objects.get()), status.HTTP_200_OK
