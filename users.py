import os
from sqlalchemy.sql import text
from flask import abort, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from db import db

def login(username, password):
    sql = 'SELECT password, id, name, role FROM users WHERE username=:username'
    result = db.session.execute(text(sql), {'username':username})
    user = result.fetchone()
    if not user:
        return False
    if not check_password_hash(user[0], password):
        return False
    session['user_id'] = user[1]
    session['user_name'] = user[2]
    session['user_role'] = user[3]
    session['csrf_token'] = os.urandom(16).hex()
    return True

def logout():
    del session['user_id']
    del session['user_name']
    del session['user_role']

def register(name, username, password, role):
    hash_value = generate_password_hash(password)
    try:
        sql = '''INSERT INTO users (name, username, password, role)
                 VALUES (:name, :username, :password, :role)'''
        db.session.execute(text(sql),
                           {'name':name, 'username':username, 'password':hash_value, 'role':role})
        db.session.commit()
    except:
        return False
    return login(username, password)

def user_id(username=None):
    if username:
        sql = 'SELECT id from users WHERE username=:username'
        return db.session.execute(text(sql), {'username': username}).fetchone()[0]
    return session.get('user_id', 0)

def require_role(role):
    if role > session.get('user_role', 0):
        abort(403)

def check_csrf():
    if session['csrf_token'] != request.form['csrf_token']:
        abort(403)
