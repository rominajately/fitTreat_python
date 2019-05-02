from flask import render_template, redirect, url_for, jsonify, request
from app import app
from app.controller import user_controller, appData_controller, symptom_controller, meal_controller
from app.models.user import User
from mongoengine import DoesNotExist
from datetime import datetime, timedelta
from flask_api import status

# API Endpoints to be used in Android Application

''' /*** Pull Active User Details ***/ '''  # done Tested


@app.route('/api/loggedInUser/<user_id>')
def loggedInUser(user_id):
    return user_controller.activeUser(user_id)


''' /*** Send password change email to user ***/ '''


@app.route('/api/changePassword/<email>') # done - Partly Tested
def changePassword(email):
    return user_controller.changePassword(email)


''' /*** Show password change view ***/ '''


@app.route('/api/passwordResetRedirect') # done - Partly tested
def passwordResetRedirect():
    token = request.args.get('token')
    id = request.args.get('id')

    if id and token:
        try:
            user = User.objects(id=id).get()
            print('user.id', user.id)
            print('userId', id)
            print('token', token)
            print('resetPasswordToken', user.resetPasswordToken)

            if str(user.id) == id and user.resetPasswordToken == token:
                if datetime.now() < user.resetPasswordExpires:
                    resp = app.send_static_file('passwordReset/passwordReset.html')
                    resp.set_cookie('token', value=user.resetPasswordToken,
                                    expires=datetime.now() + timedelta(minutes=5))
                    return resp
                else:
                    return app.send_static_file('passwordReset/passwordLinkExpired.html')
            else:
                print('invalid token')
                return jsonify({'stat': 'Invalid token'}), status.HTTP_400_BAD_REQUEST
        except DoesNotExist:
            print('no such user found')
            return jsonify({'stat': 'No such user found'}), status.HTTP_400_BAD_REQUEST
    else:
        print('Id or token not found')
        return jsonify({'stat': 'Id or token not found'}), status.HTTP_400_BAD_REQUEST


''' /*** Reset user password ***/ '''  # done - Tested


@app.route('/api/resetPassword', methods=['POST'])
def resetPassword():
    return user_controller.resetPassword()


''' /*** Change status of message to read/unread ***/ '''  # done - Tested


@app.route('/api/readMessage/<user_id>/<msg_id>')
def readMessage(user_id, msg_id):
    return user_controller.messageReadStatusChange(user_id, msg_id)


''' /*** Update weight target ***/ '''  # done - Tested


@app.route('/api/targetWeight', methods=['PUT'])
def targetWeight():
    return user_controller.updateGoalWeight()


''' /*** Reload user messages ***/ '''  # done - Tested


@app.route('/api/reloadMessages/<id>')
def reloadMessages(id):
    return user_controller.reloadMessages(id)


''' /*** Update user profile ***/ '''  # done - Tested


@app.route('/api/updateProfile', methods=['PUT'])
def updateProfile():
    return user_controller.updateProfile()


''' /*** Update user photo ***/ '''


@app.route('/api/photoUpdate', methods=['POST'])
def photoUpdate():
    return user_controller.userPhotoUpdate()  # done - Tested


''' /*** Get meals assigned to user ***/ '''


@app.route('/api/getMeals/<userId>')
def getMeals(userId):
    return meal_controller.getMeals(userId)  # done - Tested


''' /*** Filter meals ***/ '''


@app.route('/api/filterMeals/<type>/<foodPref>/<userId>')
def filterMeals(type, foodPref, userId):
    return meal_controller.filterMeals(type, foodPref, userId)  # done - Tested


''' /* Initial Symptoms */ '''


@app.route('/api/initialSymptoms')
def initialSymptoms():
    return symptom_controller.first5Symptoms()  # done - Tested


''' /* Search Symptom */ '''


@app.route('/api/searchSymptoms/<searchParam>')
def searchSymptoms(searchParam):
    return symptom_controller.searchSymptom(searchParam=searchParam)  # done - Tested


''' /*** Get app data ***/ '''


@app.route('/api/getAppData')
def getAppData():
    return appData_controller.getAppDefaultData()  # done - Tested


''' /*** Send message to admin ***/ '''  # done


@app.route('/api/sendMsgToAdmin', methods=['POST'])
def sendMsgToAdmin():
    body = request.get_json()
    senderId = body['id']
    msg = body['msg']

    print('Admin msg sent by {}. Message: {}'.format(senderId, msg))

    return jsonify({'msg': 'Thank you for reaching out to us. Will revert asap.'})
