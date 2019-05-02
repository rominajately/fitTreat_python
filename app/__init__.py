import os
from flask import Flask
from flask_cors import CORS
from flask_mongoengine import MongoEngine
from mongoengine import DoesNotExist
from config import Config

app = Flask(__name__, static_url_path="/public", static_folder="public")
CORS(app)
app.config.from_object(Config)
mdb = MongoEngine(app)
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

from app import models
from app.jsonSerializer import Encoder
from app.routes import test_routes, admin_routes, api_routes, auth_routes

app.json_encoder = Encoder

try:
    appData = models.appData.AppData.objects.get()
    print('App data already exists. No action taken.')
except DoesNotExist:
    models.appData.AppData(
        aboutSection='<hr></hr><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras orci ante, posuere ac nulla a, sagittis dignissim lacus. Vestibulum in ullamcorper magna. Ut sem nisl, accumsan id quam ac, pulvinar gravida enim. Praesent mattis finibus velit, vehicula sodales odio blandit in. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.<p><hr></hr>',
        references='BMI Calculation Formulae : <a href="https://www.icliniq.com/tool/weight-loss-by-goal-date-calculator">icliniq.com</a><br><hr></hr>Dietary Guidelines : <a href="https://www.choosemyplate.gov/dietary-guidelines">US Department of Agriculture</a>'
    ).save()
except Exception as e:
    print('general error', e)

if __name__ == '__main__':
    pass
    # print('running on main')
else:
    pass
    # print('running on', __name__)

print('App running on port {}'.format(Config.port))
app.run(host='0.0.0.0', port=Config.port)
