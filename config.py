from cfenv import AppEnv
import os

env = AppEnv()


print(env)

# Configuration File for application variables

class Config(object): 
    #crptrKey = 'R@nd0m5tr1ngt0g3ner@t3Pa55w0rd'
    crptrKey = b'WWUV2cX5GVM5K2iFu_MauyOoecTvUNGabtpG4z8TAEY='
    port = os.getenv("PORT") or 8888
    s3URL = os.getenv("S3_URL") or 'https://s3.us-east-2.amazonaws.com/fittreatstorage/meal_images_dev/'
    userId = os.getenv("SENDGRID_USERNAME") or 'balu251994@gmail.com'
    password = os.getenv("SENDGRID_PASSWORD") or '###########'
    smtp_host = os.getenv("SMTP_HOST") or 'smtp.gmail.com'
    smtp_port = os.getenv("SMTP_PORT") or 587
    # uri = env.uris[0] or 'localhost:8888'
    uri = os.getenv("uri") or 'localhost:8888'
    dbName = os.getenv("MONGO_DB_NAME") or 'fitdb'
    mongo_host = os.getenv("MONGO_HOST") or 'mongodb://localhost:27017'
    MONGODB_SETTINGS = {
        'db': dbName,
        'host': mongo_host + '/' + dbName,
    }
