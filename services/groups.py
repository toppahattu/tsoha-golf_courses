from sqlalchemy.sql import text
from sqlalchemy import exc
from db import db

def add_group(name, description, courses):
    sql = '''INSERT INTO groups (name, description)
             VALUES (:name, :description) RETURNING id'''
    group_id = db.session.execute(text(sql), {'name': name,
                                   'description': description}).fetchone()[0]
    if group_id:
        for course_id in courses:
            if not add_course_to_group(course_id, group_id):
                return None
    db.session.commit()
    return group_id

def add_course_to_group(course_id, group_id):
    try:
        sql = '''INSERT INTO course_group (course_id, group_id)
                 VALUES (:course_id, :group_id)'''
        db.session.execute(text(sql),
                           {'course_id': course_id, 'group_id': group_id})
    except exc.SQLAlchemyError:
        return False
    return True

def edit_group(group_id, name, description, removed_courses, added_courses):
    sql = 'UPDATE groups SET name=:name, description=:description WHERE id=:group_id'
    db.session.execute(text(sql), {'name': name, 'description': description, 'group_id': group_id})
    for course_id in added_courses:
        if not add_course_to_group(course_id, group_id):
            return False
    remove_courses(group_id, removed_courses)
    return True

def get_all_groups():
    sql = 'SELECT id, name FROM groups ORDER BY name'
    return db.session.execute(text(sql)).fetchall()

def get_courses(group_id):
    sql = '''SELECT c.id, c.name FROM courses c, course_group cg
             WHERE cg.group_id=:group_id AND c.id=cg.course_id'''
    return db.session.execute(text(sql),
                              {'group_id': group_id}).fetchall()

def get_group_info(group_id):
    sql = '''SELECT name, description FROM groups
             WHERE id=:group_id'''
    return db.session.execute(text(sql),
                              {'group_id': group_id}).fetchone()

def remove_course(course_id, group_id):
    sql = '''DELETE FROM course_group
             WHERE group_id=:group_id AND course_id=:course_id'''
    db.session.execute(text(sql),
                       {'group_id': group_id, 'course_id': course_id})

def remove_courses(group_id, courses):
    for course_id in courses:
        remove_course(course_id, group_id)
    db.session.commit()

def remove_group(group_id):
    sql = 'DELETE FROM groups WHERE id=:group_id'
    db.session.execute(text(sql), {'group_id': group_id})
    db.session.commit()
