import json
from datetime import datetime

import googlemaps


with open('keys.json', 'r') as file:
	KEY = json.loads(file.read())['google']['maps']['key']

gmaps = googlemaps.Client(key=KEY)


# Координаты по адресу

address = '1600 Amphitheatre Parkway, Mountain View, CA'

coords = gmaps.geocode(address)

print(coords)

# Адрес по координатам

coords = (40.714224, -73.961452)

address = gmaps.reverse_geocode(coords)

print(address)

# Маршрут

now = datetime.now()

directions_result = gmaps.directions(
	'Sydney Town Hall',
	'Parramatta, NSW',
	mode="transit",
	departure_time=now,
)

print(directions_result)

# Матрица расстояний

origins = [
	'Perth, Australia',
	'Sydney, Australia',
	'Melbourne, Australia',
	'Adelaide, Australia',
]
destinations = [
	'Blue Mountains, Australia',
	'Bungle Bungles, Australia',
	'The Pinnacles, Australia',
]

matrix = gmaps.distance_matrix(origins, destinations)

print(matrix)

# Место в радиусе

# place = gmaps.find_place(
# 	'Restaurant',
# 	'textquery',
# 	fields=[
# 		'place_id',
# 		'geometry/location',
# 		'name',
# 		'formatted_address',
# 		'photos',
# 		'price_level',
# 		'rating',
# 		'types',
# 	],
# 	location_bias='circle:0.5@47.390325,8.515934',
# )

# print(place)

geo = {
	'lat': 47.390325,
	'lng': 8.515934,
}

radius = 1000 # в метрах

category = 'Food'

places = gmaps.places_nearby(
	location=(geo['lat'], geo['lng']),
	radius=radius,
	keyword = category,
)['results']

print(places)