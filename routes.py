from flask import render_template, request, redirect
import folium
from app import app
import courses
import users

@app.route('/')
def index():
    my_map = folium.Map(location=(60.192059, 24.945831), width=800, height=600, zoom_start=9)
    golfcourses = courses.get_coords()
    ratings = courses.get_course_ratings()
    print(ratings)
    if golfcourses:
        for course in golfcourses:
            lat_lng = course.coordinates.strip('()').split(',')
            marker = folium.Marker(
            [lat_lng[0], lat_lng[1]],
            popup=f'<a href=/course/{course.id}>{course.name}</a>')
            marker.add_to(my_map)
    my_map.save('templates/map.html')
    return render_template('index.html', ratings=ratings)

@app.route('/course/<int:course_id>')
def show_course(course_id):
    course_info = courses.get_course_info(course_id)
    course_training = courses.get_training_areas(course_id)
    course_clubhouse = courses.get_clubhouse_info(course_id)
    review = courses.get_review(course_id, users.user_id())
    return render_template('course.html', course_id=course_id, info=course_info,
                           training=course_training, clubhouse=course_clubhouse, review=review)

@app.route('/edit/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    users.require_role(2)
    if request.method == 'GET':
        course_info = courses.get_course_info(course_id)
        course_training = courses.get_training_areas(course_id)
        course_clubhouse = courses.get_clubhouse_info(course_id)
        return render_template('edit.html', course_id=course_id, info=course_info,
                               training=course_training, clubhouse=course_clubhouse)
    if request.method == 'POST':
        users.check_csrf()
        courses.edit_course(course_id)
    return redirect(f'/course/{course_id}')

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
    return redirect(f'/course/{course_id}')

@app.route('/remove', methods=['POST'])
def remove():
    users.check_csrf()
    users.require_role(2)
    if 'course' in request.form:
        course_id = request.form['course']
        if 'user' in request.form:
            user_id = users.user_id(request.form['user'])
            courses.remove_review(user_id, course_id)
            return redirect(f'/reviews/{course_id}')
        courses.remove_course(course_id)
    return redirect('/')

@app.route('/review', methods=['POST'])
def review_course():
    users.check_csrf()
    users.require_role(1)
    if 'course' in request.form:
        course_id = request.form['course']
        stars = int(request.form['rating'])
        if stars < 1 or stars > 5:
            return render_template('error.html', message='Virheellinen tähtimäärä')
        comment = request.form['comment'].strip()
        if len(comment) > 1000:
            return render_template('error.html', message='Kommentti on liian pitkä')
        if comment.strip() == '':
            comment = '-'
        if 'update' in request.form:
            courses.edit_review(users.user_id(), course_id, stars, comment)
        else:
            courses.add_review(users.user_id(), course_id, stars, comment)
    return redirect(f'/course/{course_id}')

@app.route('/reviews/<int:course_id>')
def reviews(course_id):
    all_reviews = courses.get_all_reviews(course_id)
    return render_template('reviews.html', course_id=course_id, reviews=all_reviews)

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
            return render_template('error.html',
                                   message='Käyttäjänimessä tulee olla alle 50 merkkiä')
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
        if role not in ('1', '2'):
            return render_template('error.html', message='Tuntematon käyttäjärooli')
        if not users.register(name, username, password1, role):
            return render_template('error.html', message='Rekisteröinti ei onnistunut')
    return redirect('/')
    