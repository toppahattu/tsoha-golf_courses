from flask import request
from sqlalchemy.sql import text
from geopy.geocoders import Nominatim
from db import db

def add_course():
    name = request.form['name']
    sql = 'INSERT INTO courses (name, visible) VALUES (:name, TRUE) RETURNING id'
    course_id = db.session.execute(text(sql), {'name': name}).fetchone()[0]

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