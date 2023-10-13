from flask import render_template, request, redirect
from app import app
import services.courses as courses
import services.reviews as reviews
import services.users as users

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

@app.route('/course/<int:course_id>')
def show_course(course_id):
    course_info = courses.get_course_info(course_id)
    course_layouts = courses.get_course_layouts(course_id)
    course_training = courses.get_training_areas(course_id)
    course_clubhouse = courses.get_clubhouse_info(course_id)
    review = reviews.get_review(course_id, users.user_id())
    return render_template('course.html', course_id=course_id, info=course_info,
                           layouts=course_layouts, training=course_training,
                           clubhouse=course_clubhouse, review=review)

@app.route('/courses')
def show_courses():
    all_courses = courses.get_all_courses()
    return render_template('courses.html', courses = all_courses)

@app.route('/edit/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    users.require_role(2)
    if request.method == 'GET':
        course_info = courses.get_course_info(course_id)
        course_layouts = courses.get_course_layouts(course_id)
        course_training = courses.get_training_areas(course_id)
        course_clubhouse = courses.get_clubhouse_info(course_id)
        return render_template('edit.html', course_id=course_id, info=course_info,
                               layouts=course_layouts, training=course_training,
                               clubhouse=course_clubhouse)
    if request.method == 'POST':
        users.check_csrf()
        if not courses.edit_course(course_id):
            return render_template('error.html', message='Kentän muokkaaminen ei onnistunut')
    return redirect(f'/course/{course_id}')