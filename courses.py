from flask import request
from sqlalchemy.sql import text
from geopy.geocoders import Nominatim
from db import db

def get_coords():
    sql = 'SELECT c.id, c.name, a.coordinates FROM courses c, address a WHERE c.id = a.course_id'
    return db.session.execute(text(sql))

def get_course_info(course_id):
    sql = '''SELECT c.id, c.name, c.description, a.street, a.postal_code, a.city, h.caddiemaster
             FROM courses c, address a, clubhouse h
             WHERE c.id=:course_id AND c.id=h.course_id AND c.id=a.course_id'''
    return db.session.execute(text(sql), {'course_id': course_id}).fetchone()

def get_training_areas(course_id):
    sql = '''SELECT t.has_range, t.has_practice_green, t.has_short_game_area
             FROM courses c, training_areas t WHERE c.id=:course_id AND c.id=t.course_id'''
    services = db.session.execute(text(sql), {'course_id': course_id}).fetchone()
    found_services = []
    if services.has_range:
        found_services.append('Range')
    if services.has_practice_green:
        found_services.append('Harjoitusviheriö')
    if services.has_short_game_area:
        found_services.append('Lähipelialue')
    return found_services

def get_clubhouse_info(course_id):
    sql = '''SELECT h.has_restaurant, h.has_pro_shop, h.has_locker_room, h.has_sauna
             FROM courses c, clubhouse h WHERE c.id=:course_id AND c.id=h.course_id'''
    services = db.session.execute(text(sql), {'course_id': course_id}).fetchone()
    found_services = []
    if services.has_restaurant:
        found_services.append('Ravintola')
    if services.has_pro_shop:
        found_services.append('Pro shop')
    if services.has_locker_room:
        found_services.append('Pukuhuoneet')
    if services.has_sauna:
        found_services.append('Sauna')
    return found_services

def add_course():
    name = request.form['name']
    description = request.form['description']
    sql = 'INSERT INTO courses (name, description) VALUES (:name, :description) RETURNING id'
    course_id = db.session.execute(text(sql),
                                   {'name': name,'description': description}).fetchone()[0]

    sql = '''INSERT INTO address (course_id, street, postal_code, city, coordinates)
             VALUES (:course_id, :street, :postal, :city, :coords)'''
    add_address(course_id, sql)
    sql = '''INSERT INTO training_areas (course_id, has_range,
             has_practice_green, has_short_game_area)
             VALUES (:course_id, :range, :green, :short)'''
    add_training(course_id, sql)
    sql = '''INSERT INTO clubhouse (course_id, caddiemaster, has_restaurant,
             has_pro_shop, has_locker_room, has_sauna)
             VALUES (:course_id, :caddie, :restaurant, :pro_shop, :locker, :sauna)'''
    add_clubhouse(course_id, sql)

    db.session.commit()
    return course_id

def edit_course(course_id):
    name = request.form['name']
    description = request.form['description']
    sql = 'UPDATE courses SET name=:name, description=:description WHERE id=:course_id'
    db.session.execute(text(sql),
                       {'name': name, 'description': description, 'course_id': course_id})

    sql =  '''UPDATE address SET street=:street, postal_code=:postal,
              city=:city, coordinates=:coords
              WHERE course_id=:course_id'''
    add_address(course_id, sql)
    sql = '''UPDATE training_areas SET has_range=:range,
             has_practice_green=:green, has_short_game_area=:short
             WHERE course_id=:course_id'''
    add_training(course_id, sql)
    sql = '''UPDATE clubhouse SET caddiemaster=:caddie,
             has_restaurant=:restaurant, has_pro_shop=:pro_shop,
             has_locker_room=:locker, has_sauna=:sauna
             WHERE course_id=:course_id'''
    add_clubhouse(course_id, sql)

    db.session.commit()

def add_address(course_id, sql):
    street = request.form['street']
    postal = request.form['postal']
    city = request.form['city']
    nom_client = Nominatim(user_agent='tutorial')
    location = nom_client.geocode(f'{street}, {postal} {city}').raw
    coords = f'({location["lat"]}, {location["lon"]})'
    db.session.execute(text(sql),
                       {'course_id': course_id, 'street': street,
                        'postal': postal, 'city': city, 'coords': coords})

def add_training(course_id, sql):
    training = request.form.getlist('training')
    practicerange = has_service('range', training)
    practicegreen = has_service('green', training)
    shortgame_area = has_service('short', training)
    db.session.execute(text(sql),
                       {'course_id': course_id, 'range': practicerange,
                        'green': practicegreen, 'short': shortgame_area})

def add_clubhouse(course_id, sql):
    caddie = request.form['caddie']
    club = request.form.getlist('club')
    restaurant = has_service('restaurant', club)
    pro_shop = has_service('proshop', club)
    locker = has_service('locker', club)
    sauna = has_service('sauna', club)
    db.session.execute(text(sql),
                       {'course_id': course_id, 'caddie': caddie, 'restaurant': restaurant,
                        'pro_shop': pro_shop, 'locker': locker, 'sauna': sauna})

def has_service(service, services):
    return service in services

def remove_course(course_id):
    sql = 'DELETE FROM courses WHERE id=:course_id'
    db.session.execute(text(sql), {'course_id': course_id})
    db.session.commit()

def get_review(course_id, user_id):
    sql = 'SELECT stars, comment FROM reviews WHERE user_id=:user_id AND course_id=:course_id'
    return db.session.execute(text(sql), {'user_id': user_id, 'course_id': course_id}).fetchone()

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

def remove_review(user_id, course_id):
    sql = 'DELETE FROM reviews WHERE user_id=:user_id AND course_id=:course_id'
    db.session.execute(text(sql), {'user_id': user_id, 'course_id': course_id})
    db.session.commit()

def get_all_reviews(course_id):
    sql = '''SELECT c.name AS c_name, u.name AS u_name, u.username, r.id, r.stars, r.comment
             FROM courses c, reviews r, users u
             WHERE c.id=:course_id AND r.user_id=u.id AND r.course_id=:course_id ORDER BY r.id'''
    return db.session.execute(text(sql), {'course_id': course_id}).fetchall()
