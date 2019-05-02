from flask import render_template, redirect, url_for, jsonify, request
from app import app, bcrypt
from app.controller import user_controller
import flask_bcrypt
from app.models.user import User
from mongoengine.errors import DoesNotExist
from flask_api import status

''' /*** API Route to test application ***/ '''
@app.route('/auth/test')
def test():
    str = 'Test'
    generated = flask_bcrypt.generate_password_hash(str, 5)
    print(generated)
    if flask_bcrypt.check_password_hash(generated, 'Test1'):
        return 'Password Match'
    else:
        return 'Password Mis-match'


''' /*** User Registration ***/ '''  # done - Tested


@app.route('/auth/register', methods=['POST'])
def register():
    return user_controller.register()


''' /*** User Login ***/ '''  # done - Tested


@app.route('/auth/login', methods=['POST'])
def login():
    # Retrieve Email and Password
    email_id = request.get_json()['email']
    password = request.get_json()['password']
    try:
        user = User.objects(email=email_id).get()
        if bcrypt.check_password_hash(user['password'], password):
            ''' Checks password - If correct login is successful '''
            user['password'] = None
            user['mealAssigned'] = None
            unreadMsg = [msg for msg in user['messages'] if msg['readFlag'] is False]
            user['unreadCount'] = len(unreadMsg)
            return jsonify(user), status.HTTP_200_OK
        else:
            return jsonify({'error': 'Invalid Credentials'}), status.HTTP_401_UNAUTHORIZED
            ''' returns response if credentials invalid '''
    except DoesNotExist:
        ''' returns response if User ID doesn't exist in database '''
        return jsonify({'error': 'User does not exist'}), status.HTTP_401_UNAUTHORIZED
