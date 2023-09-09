from flask import request
from sqlalchemy.sql import text
from geopy.geocoders import Nominatim
from db import db

def get_course_info(course_id):
    sql = '''SELECT c.id, c.name, c.description, a.street, a.postal_code, a.city, h.caddie_master     
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
        found_services.append('Practice green')
    if services.has_short_game_area:
        found_services.append('Short game area')
    return found_services

def get_clubhouse_info(course_id):
    sql = '''SELECT h.has_restaurant, h.has_pro_shop, h.has_locker_room, h.has_sauna
             FROM courses c, clubhouse h WHERE c.id=:course_id AND c.id=h.course_id'''
    services = db.session.execute(text(sql), {'course_id': course_id}).fetchone()

    found_services = []
    if services.has_restaurant:
        found_services.append('Restaurant')
    if services.has_pro_shop:
        found_services.append('Pro shop')
    if services.has_locker_room:
        found_services.append('Locker rooms')
    if services.has_sauna:
        found_services.append('Sauna')
    return found_services

def add_course():
    name = request.form['name']
    description = request.form['description']
    sql = 'INSERT INTO courses (name, description) VALUES (:name, :description) RETURNING id'
    course_id = db.session.execute(text(sql), {'name': name, 'description': description}).fetchone()[0]

    street = request.form['street']
    postal = request.form['postal']
    city = request.form['city']
    nom_client = Nominatim(user_agent='tutorial')
    location = nom_client.geocode(f'{street}, {postal} {city}').raw
    coords = f'({location["lat"]}, {location["lon"]})'
    sql = '''INSERT INTO address (course_id, street, postal_code, city, coordinates) 
             VALUES (:course_id, :street, :postal, :city, :coords)'''
    db.session.execute(text(sql), {'course_id': course_id, 'street': street, 'postal': postal, 'city': city, 'coords': coords})

    training = request.form.getlist('training')
    range = has_service('range', training)
    green = has_service('green', training)
    short = has_service('short', training)
    sql = '''INSERT INTO training_areas (course_id, has_range, has_practice_green, has_short_game_area) 
             VALUES (:course_id, :range, :green, :short)'''
    db.session.execute(text(sql), {'course_id': course_id, 'range': range, 'green': green, 'short': short})

    caddie = request.form['caddie']
    club = request.form.getlist('club')
    restaurant = has_service('restaurant', club)
    pro_shop = has_service('proshop', club)
    locker = has_service('locker', club)
    sauna = has_service('sauna', club)
    sql = '''INSERT INTO clubhouse (course_id, caddie_master, has_restaurant, has_pro_shop, has_locker_room, has_sauna) 
             VALUES (:course_id, :caddie, :restaurant, :pro_shop, :locker, :sauna)'''
    db.session.execute(text(sql), {'course_id': course_id, 'caddie': caddie, 'restaurant': restaurant, 'pro_shop': pro_shop, 'locker': locker, 'sauna': sauna})

    db.session.commit()
    return course_id

def has_service(service, services):
    return (True if service in services else False)

def remove_course(course_id):
    sql = 'DELETE FROM courses WHERE id=:course_id'
    db.session.execute(text(sql), {'course_id': course_id})
    db.session.commit()
