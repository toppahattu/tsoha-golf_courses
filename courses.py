from flask import request
from sqlalchemy.sql import text
from geopy.geocoders import Nominatim
from db import db

def search_courses():
    name = request.form['name'].strip().upper()
    city = request.form['city'].strip().upper()
    services = request.form.getlist('services')
    practicerange = has_service('range', services)
    practicegreen = has_service('green', services)
    shortgame_area = has_service('short', services)
    restaurant = has_service('restaurant', services)
    pro_shop = has_service('proshop', services)
    sauna = has_service('sauna', services)

    services = {
        'tr.has_range': practicerange,
        'tr.has_practice_green': practicegreen,
        'tr.has_short_game_area': shortgame_area,
        'ch.has_restaurant': restaurant,
        'ch.has_pro_shop': pro_shop,
        'ch.has_sauna': sauna
    }
    sql_help = ''
    sql_params = {}
    if len(name):
        sql_params.update({'name': '%'+name+'%'})
        sql_help += f'upper(c.name) LIKE :name'
        if len(city):
            sql_help += f' AND upper(a.city) LIKE :city'
            sql_params.update({'city': '%'+city+'%'})
    elif len(city):
        sql_help += f'upper(a.city) LIKE :city'
        sql_params.update({'city': '%'+city+'%'})
    for key, value in services.items():        
        if value:
            sql_help += f' AND {key}=:{key[3:]}'
            sql_params.update({key[3:]: value})
    if not len(name) and not len(city):
        index = sql_help.find(' AND ')
        sql_help = sql_help[0:index] + sql_help[index + 5:]
    sql = f'''SELECT c.id, c.name FROM courses c, address a, training_areas tr, clubhouse ch
              WHERE c.id = a.course_id AND c.id = tr.course_id AND c.id = ch.course_id AND {sql_help}'''
    return db.session.execute(text(sql), sql_params).fetchall()

def get_coords():
    sql = 'SELECT c.id, c.name, a.coordinates FROM courses c, address a WHERE c.id = a.course_id'
    return db.session.execute(text(sql))

def get_course_info(course_id):
    sql = '''SELECT c.id, c.name, c.description, c.www, a.street, a.postal_code, a.city, h.caddiemaster
             FROM courses c, address a, clubhouse h
             WHERE c.id=:course_id AND c.id=h.course_id AND c.id=a.course_id'''
    return db.session.execute(text(sql), {'course_id': course_id}).fetchone()

def get_course_layouts(course_id):
    sql = '''SELECT c.id, c.name, c.par, c.holes FROM courses cs, course c
             WHERE cs.id=:course_id AND cs.id=c.course_id'''
    return db.session.execute(text(sql), {'course_id': course_id}).fetchall()

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
    description = request.form['description'].strip()
    www = request.form['www']
    sql = 'INSERT INTO courses (name, description, www) VALUES (:name, :description, :www) RETURNING id'
    course_id = db.session.execute(text(sql),
                                   {'name': name,'description': description, 'www': www}).fetchone()[0]

    if course_id:
        success = False

        sql = '''INSERT INTO address (course_id, street, postal_code, city, coordinates)
                 VALUES (:course_id, :street, :postal, :city, :coords)'''
        success = add_address(course_id, sql)
        if not success:
            return None
        
        sql = '''INSERT INTO course (course_id, name, par, holes)
                 VALUES (:course_id, :name, :par, :holes)'''
        success = add_layouts(course_id, sql)
        if not success:
            return None

        sql = '''INSERT INTO training_areas (course_id, has_range,
                 has_practice_green, has_short_game_area)
                 VALUES (:course_id, :range, :green, :short)'''
        success = add_training(course_id, sql)
        if not success:
            return None

        sql = '''INSERT INTO clubhouse (course_id, caddiemaster, has_restaurant,
                 has_pro_shop, has_locker_room, has_sauna)
                 VALUES (:course_id, :caddie, :restaurant, :pro_shop, :locker, :sauna)'''
        success = add_clubhouse(course_id, sql)
        if not success:
            return None
            
    db.session.commit()
    return course_id

def edit_course(course_id):
    name = request.form['name']
    description = request.form['description'].strip()
    www = request.form['www']
    success = False
    sql = 'UPDATE courses SET name=:name, description=:description, www=:www WHERE id=:course_id'
    try:
        db.session.execute(text(sql),
                       {'name': name, 'description': description, 'www': www, 'course_id': course_id})
    except:
        return False

    sql =  '''UPDATE address SET street=:street, postal_code=:postal,
              city=:city, coordinates=:coords
              WHERE course_id=:course_id'''
    success = add_address(course_id, sql)
    if not success:
        return False
    
    sql = '''INSERT INTO course (course_id, name, par, holes)
                 VALUES (:course_id, :name, :par, :holes)'''
    success = add_layouts(course_id, sql)
    if not success:
        return False

    sql = '''UPDATE training_areas SET has_range=:range,
             has_practice_green=:green, has_short_game_area=:short
             WHERE course_id=:course_id'''
    success = add_training(course_id, sql)
    if not success:
        return False

    sql = '''UPDATE clubhouse SET caddiemaster=:caddie,
             has_restaurant=:restaurant, has_pro_shop=:pro_shop,
             has_locker_room=:locker, has_sauna=:sauna
             WHERE course_id=:course_id'''
    success = add_clubhouse(course_id, sql)
    if not success:
        return False

    db.session.commit()
    return success

def add_address(course_id, sql):
    street = request.form['street']
    postal = request.form['postal']
    city = request.form['city']
    nom_client = Nominatim(user_agent='tutorial')
    location = nom_client.geocode(f'{street}, {postal} {city}').raw
    coords = f'({location["lat"]}, {location["lon"]})'
    try:
        db.session.execute(text(sql),
                       {'course_id': course_id, 'street': street,
                        'postal': postal, 'city': city, 'coords': coords})
    except:
        return False
    return True

def add_layouts(course_id, sql):
    names = request.form.getlist('layoutname')
    pars = request.form.getlist('layoutpar')
    hole_counts = request.form.getlist('layoutholes')
    for i in range(len(names)):
        name = names[i].strip()
        par = pars[i]
        holes = hole_counts[i]
        if len(name):
            try:
                db.session.execute(text(sql),
                               {'course_id': course_id, 'name': name, 'par': par,
                                'holes': holes})
            except:
                return False
    return True

def add_training(course_id, sql):
    training = request.form.getlist('training')
    practicerange = has_service('range', training)
    practicegreen = has_service('green', training)
    shortgame_area = has_service('short', training)
    try:
        db.session.execute(text(sql),
                       {'course_id': course_id, 'range': practicerange,
                        'green': practicegreen, 'short': shortgame_area})
    except:
        return False
    return True

def add_clubhouse(course_id, sql):
    caddie = request.form['caddie']
    club = request.form.getlist('club')
    restaurant = has_service('restaurant', club)
    pro_shop = has_service('proshop', club)
    locker = has_service('locker', club)
    sauna = has_service('sauna', club)
    try:
        db.session.execute(text(sql),
                       {'course_id': course_id, 'caddie': caddie, 'restaurant': restaurant,
                        'pro_shop': pro_shop, 'locker': locker, 'sauna': sauna})
    except:
        return False
    return True

def has_service(service, services):
    return service in services

def remove_course(course_id):
    sql = 'DELETE FROM courses WHERE id=:course_id'
    db.session.execute(text(sql), {'course_id': course_id})
    db.session.commit()

def remove_layout(layout_id):
    sql = 'DELETE FROM course WHERE id=:layout_id'
    db.session.execute(text(sql), {'layout_id': layout_id})
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

def get_course_ratings():
    sql = '''SELECT c.name, CAST(COALESCE(AVG(r.stars), 0) AS DECIMAL(3, 2)) AS stars, c.id
             FROM courses c LEFT JOIN reviews r ON c.id=r.course_id GROUP BY c.id, c.name ORDER BY stars DESC'''
    return db.session.execute(text(sql)).fetchall()
