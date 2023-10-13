from flask import render_template, request, redirect
from app import app
import services.courses as courses
import services.groups as groups
import services.users as users

@app.route('/addgroup', methods=['GET', 'POST'])
def add_group():
    users.require_role(2)
    if request.method == 'GET':
        all_courses = courses.get_all_courses()
        return render_template('addgroup.html', courses=all_courses)
    if request.method == 'POST':
        users.check_csrf()
        name = request.form['name'].strip()
        description = request.form['description'].strip()
        selected_courses = request.form.getlist('courses')
        group_id = groups.add_group(name, description, selected_courses)
        if not group_id:
            return render_template('error.html', message='Ryhmän lisääminen ei onnistunut')
    return redirect(f'/group/{group_id}')

@app.route('/editgroup/<int:group_id>', methods=['GET', 'POST'])
def edit_group(group_id):
    users.require_role(2)
    groups_courses = groups.get_courses(group_id)
    if request.method == 'GET':
        group_info = groups.get_group_info(group_id)
        all_courses = courses.get_all_courses()
        return render_template('editgroup.html', group_id=group_id, group=group_info,
                               all_courses=all_courses, groups_courses=groups_courses)
    if request.method == 'POST':
        users.check_csrf()
        name = request.form['name'].strip()
        description = request.form['description'].strip()
        selected_courses = request.form.getlist('courses')
        groups_ids = list(map(lambda x: str(x[0]), groups_courses))
        removed_courses = [course for course in groups_ids if course not in selected_courses]
        added_courses = [course for course in selected_courses if course not in groups_ids]
        if not groups.edit_group(group_id, name, description, removed_courses, added_courses):
            return render_template('error.html', message='Ryhmän muokkaaminen ei onnistunut')
    return redirect(f'/group/{group_id}')

@app.route('/group/<int:group_id>')
def show_group(group_id):
    info = groups.get_group_info(group_id)
    groups_courses = groups.get_courses(group_id)
    return render_template('/group.html', group_id=group_id, group=info, courses=groups_courses)

@app.route('/groups')
def show_groups():
    all_groups = groups.get_all_groups()
    return render_template('groups.html', groups=all_groups)