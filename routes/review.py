from flask import render_template, request, redirect
from app import app
import services.courses as courses
import services.reviews as reviews
import services.users as users

@app.route('/review', methods=['POST'])
def review_course():
    users.check_csrf()
    users.require_role(1)
    if 'course' in request.form:
        course_id = request.form['course']
        stars = int(request.form['rating'])
        comment = request.form['comment'].strip()        
        if comment == '':
            comment = '-'
        message = reviews.validate_review(stars, comment)
        if message:
            return render_template('error.html', message=message)
        if 'update' in request.form:
            reviews.edit_review(users.user_id(), course_id, stars, comment)
        else:
            reviews.add_review(users.user_id(), course_id, stars, comment)
    return redirect(f'/course/{course_id}?status=reviewed')

@app.route('/reviews/<int:course_id>')
def show_reviews(course_id):
    all_reviews = reviews.get_all_reviews(course_id)
    course_info = courses.get_course_info(course_id)
    return render_template('reviews.html', course_id=course_id,
                           reviews=all_reviews, name=course_info.name)