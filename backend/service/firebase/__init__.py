from firebase_admin import credentials, initialize_app

from .auth import authenticate, register, send_password_reset_email, verify_password_reset_code
from .crud_user import list_user, read_user, create_user, update_user, delete_user
import json
import pyrebase

__all__ = [
    'register',
    'authenticate',
    'send_password_reset_email',
    'verify_password_reset_code',
    'list_user',
    'read_user',
    'create_user',
    'update_user',
    'pb',
]


try:
    credential = credentials.Certificate('firebase_private.json')
    initialize_app(credential)
except:
    raise Exception("Error when initializing firebase-admin credential")

try:
    pb = pyrebase.initialize_app(json.load(open('firebase_config.json')))
except:
    raise Exception("Error when initializing pyrebase credential")