from flask import render_template, request
import folium
from app import app
import services.courses as courses

@app.route('/', methods=['GET', 'POST'])
def index():
    my_map = folium.Map(location=(60.192059, 24.945831), width='100%', height=600, zoom_start=9)
    golfcourses = courses.get_coords()
    ratings = courses.get_all_course_ratings()
    if golfcourses:
        for course in golfcourses:
            lat_lng = course.coordinates.strip('()').split(',')
            marker = folium.Marker(
            [lat_lng[0], lat_lng[1]],
            popup=f'<a href=/course/{course.id}>{course.name}</a>')
            marker.add_to(my_map)
    my_map.save('templates/map.html')
    if request.method == 'POST':
        results = courses.search_courses()
        if not results:
            no_results = True
        return render_template('index.html', ratings=ratings, results=results, no_results=no_results)
    return render_template('index.html', ratings=ratings)