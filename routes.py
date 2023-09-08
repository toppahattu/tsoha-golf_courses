from app import app
from flask import render_template, request, redirect
import folium
import courses
import users

@app.route('/')
def index():
    map = folium.Map(location=(60.192059, 24.945831), width=800, height=600, zoom_start=11)
    map.save('templates/map.html')
    return render_template('index.html')

@app.route('/course/<int:course_id>')
def show_course():
    return render_template('course.html')

@app.route('/add', methods=['GET', 'POST'])
def add_course():
    users.require_role(2)
    if request.method == 'GET':
        return render_template('add.html')
    if request.method == 'POST':
        users.check_csrf()
        course_id = courses.add_course()
        if not course_id:
            return render_template('error.html', message='Kentän lisääminen ei onnistunut')
        return redirect('/') #(f'/course/{course_id}')

@app.route('/logout')
def logout():
    users.logout()
    return redirect('/')

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
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('/register.html')
    
    if request.method == 'POST':
        name = request.form['name']
        if len(name) > 50:
            return render_template('error.html', message='Käyttäjänimessä tulee olla alle 50 merkkiä')

        username = request.form['username']
        if len(username) < 3 or len(username) > 20:
            return render_template('error.html', message='Käyttäjänimessä tulee olla 3-20 merkkiä')

        password1 = request.form['password1']
        password2 = request.form['password2']
        if password1 != password2:
            return render_template('error.html', message='Salasanat eroavat toisistaan')
        if len(password1.strip()) == 0:
            return render_template('error.html', message='Salasana ei voi olla tyhjä')

        role = request.form['role']
        #TODO: mahdollinen validation

        if not users.register(name, username, password1, role):
            return render_template('error.html', message='Rekisteröinti ei onnistunut')
        return redirect('/')
        