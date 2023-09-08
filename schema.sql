CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    username TEXT UNIQUE,
    password TEXT,
    role INTEGER
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name TEXT,
    visible BOOLEAN
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    course_id INTEGER,
    stars INTEGER,
    comment TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (course_id) REFERENCES courses (id)
);

CREATE TABLE training_areas (
    id SERIAL PRIMARY KEY,
    course_id INTEGER,
    has_range BOOLEAN,
    has_practice_green BOOLEAN,
    has_short_game_area BOOLEAN,
    FOREIGN KEY (course_id) REFERENCES courses (id)
);

CREATE TABLE clubhouse (
    id SERIAL PRIMARY KEY,
    course_id INTEGER,
    caddie_master VARCHAR(20) CHECK (caddie_master LIKE '+358%'),
    has_restaurant BOOLEAN,
    has_pro_shop BOOLEAN,
    has_locker_room BOOLEAN,
    has_sauna BOOLEAN,
    FOREIGN KEY (course_id) REFERENCES courses (id)
);

CREATE TABLE course (
    id SERIAL PRIMARY KEY,
    course_id INTEGER,
    name TEXT,
    par INTEGER,
    holes INTEGER,
    FOREIGN KEY (course_id) REFERENCES courses (id)
);

CREATE TABLE address (
    id SERIAL PRIMARY KEY,
    course_id INTEGER,
    street TEXT,
    postal_code VARCHAR(5),
    city TEXT,
    coordinates POINT,
    FOREIGN KEY (course_id) REFERENCES courses (id)
);

CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT
);

CREATE TABLE course_group (
    course_id INTEGER,
    group_id INTEGER,
    PRIMARY KEY (course_id, group_id),
    FOREIGN KEY (course_id) REFERENCES courses (id),
    FOREIGN KEY (group_id) REFERENCES groups (id)
);