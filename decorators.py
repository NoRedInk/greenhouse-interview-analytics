# -*- coding: utf-8 -*-
# http://flask.pocoo.org/snippets/8/
from functools import wraps
from flask import request, Response, current_app


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    if current_app.config['BASIC_AUTH_USERNAME'] is None or current_app.config['BASIC_AUTH_PASSWORD']is None:
        return True
    return current_app.config['BASIC_AUTH_USERNAME'] == username and current_app.config['BASIC_AUTH_PASSWORD'] == password


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
