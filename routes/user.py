from flask import render_template, request, redirect
from app import app
import services.users as users

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not users.login(username, password):
            return render_template('error.html', message='Väärä käyttäjänimi tai salasana')
    return redirect('/')

@app.route('/logout')
def logout():
    users.logout()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('/register.html')
    if request.method == 'POST':
        user_info = {'name': request.form['name'].strip(),
                     'username': request.form['username'].strip(),
                     'password1': request.form['password1'].strip(),
                     'password2': request.form['password2'].strip(),
                     'role': request.form['role']
                     }
        message = users.validate_user(user_info)
        if message:
            return render_template('error.html', message=message)
        if not users.register(user_info['name'],
                              user_info['username'],
                              user_info['password1'],
                              user_info['role']):
            return render_template('error.html', message='Rekisteröinti ei onnistunut')
    return redirect('/')