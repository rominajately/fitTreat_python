'''
Created on 19-Dec-2018
'''

import bson
from flask import request, render_template
from flask.json import jsonify
from app import app
from app.models.user import User, Messages
from attrdict import AttrDict
from datetime import datetime, timedelta
from mongoengine import DoesNotExist
from cryptography.fernet import Fernet
from config import Config
from flask_api import status

import smtplib
from email.mime.text import MIMEText

'''    
Context - Android Application
/*** New Registration ***/ 
'''


def register():
    data = AttrDict(request.get_json())
    try:
        user = User.objects(email=data.email).get()
        print(data.email + " : Email already in use")
        obj = {
            'error': "Email already in use"
        }
        return jsonify(obj), status.HTTP_400_BAD_REQUEST
    except DoesNotExist:
        print("Creating new user")
        msg_content = "Dear " + data.firstName + ", <br><br> Welcome to FitTreat.<br><br> Team FitTreat"
        try:
            user = User(
                firstName=data.firstName,
                lastName=data.lastName,
                email=data.email,
                gender=data.gender,
                password=data.password,
                dateOfBirth=data.dateOfBirth,
                # age=data.age if data.age else 0,
                weight=data.weight,
                weightUnit=data.weightUnit,
                height=data.height,
                heightUnit=data.heightUnit,
                foodPreference=data.foodPreference,
                timeZone=data.timeZone,
                medicalCondition=data.medicalCondition,
                messages=[Messages(subject="Welcome", content=msg_content)]
            )
            user = user.save()
            user['password'] = None
            unreadMsg = [msg for msg in user['messages'] if msg['readFlag'] is False]
            user['unreadCount'] = len(unreadMsg)
            return jsonify(user), status.HTTP_200_OK
        except Exception as e:
            print("Error in user registration :" + format(e))
            obj = {
                'error': "Some error occurred"
            }
            return jsonify(obj), status.HTTP_500_INTERNAL_SERVER_ERROR


''' /*** Returns Active User Details ***/ '''


def activeUser(user_id):
    try:
        user = User.objects.get(id=bson.objectid.ObjectId(str(user_id)))
        user['password'] = None
        user['mealAssigned'] = None
        unreadMsg = [msg for msg in user['messages'] if msg['readFlag'] is False]
        user['unreadCount'] = len(unreadMsg)
        return jsonify(user), status.HTTP_200_OK
    except DoesNotExist as e:
        print("Error occurred in activeUser method : " + format(e))
        return jsonify({'stat': 'Some error occurred : ' + format(e)}), status.HTTP_400_BAD_REQUEST


''' 
Context - Android Application
/*** Updates message read/unread status ***/ 
Used to mark messages in the inbox as Read/Unread
'''


def messageReadStatusChange(user_id, msg_id):
    try:
        user = User.objects.get(id=bson.objectid.ObjectId(str(user_id)))
        # message = [msg for msg in user['messages']]
        for msg in user['messages']:
            if str(msg['_id']) == msg_id:
                print('Message Found')
                msg['readFlag'] = not (msg['readFlag'])
                try:
                    msg.save()
                    return jsonify(msg)
                except Exception as e:
                    print("Error in saving message status : " + format(e))
                    return 'Error in saving message status'
    except Exception as e:
        print("Error in message read status : " + format(e))
        return jsonify({'stat': 'Some error occurred', 'error': format(e)}), status.HTTP_500_INTERNAL_SERVER_ERROR

''' 
Context - Android Application
API to update goal weight/target weight
'''
def updateGoalWeight():
    body = AttrDict(request.get_json())
    try:
        User.objects(id=body.id).update_one(targetWeight=int(body.targetWeight),
                                            targetDate=body.targetDate, targetCalories=int(body.targetCalories),
                                            weightUnit=body.weightUnit)

        return jsonify({'status': 'success'}), status.HTTP_200_OK
    except DoesNotExist:
        return jsonify({'stat': 'No such user found'}), status.HTTP_400_BAD_REQUEST

''' 
Context - Android Application
API to reload messages in the inbox
'''
def reloadMessages(id):
    try:
        user = User.objects(id=id).get()

        return jsonify({
            'msgSummary': {'totalCount':len(list(user.messages)),'unreadCount':user.unreadCount},
            'messages': user.messages
        }), status.HTTP_200_OK
    except DoesNotExist:
        return jsonify({'stat': 'No such user found'}), status.HTTP_400_BAD_REQUEST

''' 
Context - Android Application
Method to update user profile
'''
def updateProfile():
    body = AttrDict(request.get_json())
    user = User.objects(id=body.id).get();
    try:
        if user['foodPreference'] != body.foodPreference or user['medicalCondition'] != body.medicalCondition:
            user.modify(
                weight=body.weight,
                weightUnit=body.weightUnit,
                height=body.height,
                heightUnit=body.heightUnit,
                foodPreference=body.foodPreference,
                medicalCondition=body.medicalCondition,
                firstName=body.firstName,
                lastName=body.lastName,
                mealExpiry=None,
                mealAssigned=[]
            )
        else:
            user.modify(
                weight=body.weight,
                weightUnit=body.weightUnit,
                height=body.height,
                heightUnit=body.heightUnit,
                foodPreference=body.foodPreference,
                medicalCondition=body.medicalCondition,
                firstName=body.firstName,
                lastName=body.lastName,
            )
        return activeUser(body.id)
    except Exception as e:
        print("Error occurred in profile update : " + format(e))
        return jsonify({'error': 'Some error occurred'}), status.HTTP_500_INTERNAL_SERVER_ERROR


''' 
Context - Android Application
Method to update user photo
'''
def userPhotoUpdate():
    body = AttrDict(request.get_json())

    try:
        upd = User.objects(id=body.id).update_one(userPhoto=body.userPhoto)
        if upd:
            return jsonify({'id': body.id, 'photoString': body.userPhoto}), status.HTTP_200_OK
        else:
            return jsonify({'msg': 'Cannot update profile photo'}), status.HTTP_500_INTERNAL_SERVER_ERROR
    except DoesNotExist:
        return jsonify({'stat': 'No such user found'}), status.HTTP_400_BAD_REQUEST

''' 
Context - Android Application
Method to change user password
'''
def changePassword(email):
    try:
        user = User.objects(email=email).get()
        print(user)

        userId = user.id
        fern = Fernet(Config.crptrKey)
        resetToken = fern.encrypt('{}r353tT0k3n'.format(userId).encode()).decode('utf-8')
        resetExpiryTime = datetime.now() + timedelta(minutes=30)

        User.objects(id=userId) \
            .update_one(resetPasswordToken=resetToken, resetPasswordExpires=resetExpiryTime)

        userName = user.firstName
        link = "http://" + Config.uri + "/api/passwordResetRedirect?token=" + resetToken + "&id=" + str(userId)

        # return render_template('changePassword.html', username=userName, link=link)

        msg = MIMEText(render_template('changePassword.html', username=userName, link=link), 'html')
        msg['Subject'] = 'FitTreat : Password Reset'
        msg['From'] = 'FitTreat ' + Config.userId
        msg['To'] = email

        try:
            s = smtplib.SMTP(Config.smtp_host, Config.smtp_port)
            s.ehlo()
            s.starttls()
            s.login(Config.userId, Config.password)
            s.sendmail(Config.userId, [email], msg.as_string())
            s.close()
            print('mail sent')
            return jsonify({'msg': 'Please check your registered email'}), status.HTTP_200_OK
        except Exception as e:
            print('error while sending mail')
            print(e)
            return jsonify({'msg': 'Some error occurred.'}), status.HTTP_400_BAD_REQUEST
    except DoesNotExist:
        return jsonify({'stat': 'No user found with email - {}'.format(email)}), status.HTTP_404_NOT_FOUND

''' 
Context - Android Application
Method to reset password of the user
-Called from external link which user receives in the email
'''
def resetPassword():
    try:
        body = AttrDict(request.get_json())

        token = body.token
        dob = body.dob
        password = body.password

        fern = Fernet(Config.crptrKey)
        decryptToken = fern.decrypt(token.encode()).decode()

        userId = decryptToken[0:decryptToken.index("r353tT0k3n")]

        print(userId)

        try:
            user = User.objects(id=userId).get()

            if datetime.now() < user.resetPasswordExpires:
                if user.dateOfBirth == dob:
                    # user = User.objects(id=userId).get().update_one(password=password, resetPasswordExpires=datetime.now())
                    user['password'] = password
                    try:
                        user.save()
                        return app.send_static_file('passwordReset/passwordChangeSuccess.html')
                    except Exception as e:
                        print(format(e))
                        return jsonify({'Error' : format(e)}),status.HTTP_500_INTERNAL_SERVER_ERROR
                else:
                    return jsonify({'msg': 'DOB did not match'}), status.HTTP_400_BAD_REQUEST
            else:
                return app.send_static_file('passwordReset/passwordLinkExpired.html')

        except DoesNotExist:
            return jsonify({'stat': 'No such user found'}), status.HTTP_400_BAD_REQUEST
    except Exception as e:
        print(e)
        return jsonify({'stat': 'Something wrong happened'}), status.HTTP_500_INTERNAL_SERVER_ERROR
