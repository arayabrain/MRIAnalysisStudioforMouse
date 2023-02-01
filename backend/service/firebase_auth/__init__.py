import json

import pyrebase
from firebase_admin import credentials, initialize_app

from .auth import authenticate, register, send_password_reset_email, verify_password_reset_code, delete_user


__all__ = [
    'register',
    'authenticate',
    'send_password_reset_email',
    'verify_password_reset_code',
    'delete_user',
]

try:
    credential = credentials.Certificate('./credential.json')
    initialize_app(credential)
except:
    raise Exception("Error when initializing firebase-admin credential")

try:
    pb = pyrebase.initialize_app(json.load(open('./firebase_config.json')))
except:
    raise Exception("Error when initializing pyrebase credential")

