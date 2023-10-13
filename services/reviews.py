from sqlalchemy.sql import text
from db import db

def add_review(user_id, course_id, stars, comment):
    sql = '''INSERT INTO reviews (user_id, course_id, stars, comment)
             VALUES (:user_id, :course_id, :stars, :comment)'''
    db.session.execute(text(sql),
                       {'user_id': user_id, 'course_id': course_id,
                        'stars': stars, 'comment': comment})
    db.session.commit()

def edit_review(user_id, course_id, stars, comment):
    sql = '''UPDATE reviews SET stars=:stars, comment=:comment
             WHERE user_id=:user_id AND course_id=:course_id'''
    db.session.execute(text(sql), {'stars': stars, 'comment': comment,
                                   'user_id': user_id, 'course_id': course_id})
    db.session.commit()

def get_all_reviews(course_id):
    sql = '''SELECT c.name AS c_name, u.name AS u_name, u.username, r.id, r.stars, r.comment
             FROM courses c, reviews r, users u
             WHERE c.id=:course_id AND r.user_id=u.id AND r.course_id=:course_id ORDER BY r.id'''
    return db.session.execute(text(sql), {'course_id': course_id}).fetchall()

def get_review(course_id, user_id):
    sql = 'SELECT stars, comment FROM reviews WHERE user_id=:user_id AND course_id=:course_id'
    return db.session.execute(text(sql), {'user_id': user_id, 'course_id': course_id}).fetchone()


def remove_review(user_id, course_id):
    sql = 'DELETE FROM reviews WHERE user_id=:user_id AND course_id=:course_id'
    db.session.execute(text(sql), {'user_id': user_id, 'course_id': course_id})
    db.session.commit()
