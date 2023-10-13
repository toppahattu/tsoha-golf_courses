from flask import request, redirect
from app import app
import services.courses as courses
import services.groups as groups
import services.reviews as reviews
import services.users as users

@app.route('/remove', methods=['POST'])
def remove():
    users.check_csrf()
    users.require_role(2)
    if 'course' in request.form:
        course_id = request.form['course']
        if 'user' in request.form:
            user_id = users.user_id(request.form['user'])
            reviews.remove_review(user_id, course_id)
            return redirect(f'/reviews/{course_id}')
        if 'layout' in request.form:
            layout_id = request.form['layout']
            courses.remove_layout(layout_id)
            return redirect(f'/edit/{course_id}')
        courses.remove_course(course_id)
    if 'group' in request.form:
        group_id = request.form['group']
        groups.remove_group(group_id)
    return redirect('/')