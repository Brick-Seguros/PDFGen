from functools import wraps
from flask import request, abort, jsonify
from concurrent.futures import ThreadPoolExecutor
import requests
from datetime import datetime
import config
from itertools import repeat
import logging
# The actual decorator function


def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        key=config.microservices_key
        #if request.args.get('key') and request.args.get('key') == key:
        if request.headers.get('x-api-key') and request.headers.get('x-api-key') == key:
            return view_function(*args, **kwargs)
        else:
            return jsonify({'message':'AUTHORIZATION_ERROR'}),401
    return decorated_function