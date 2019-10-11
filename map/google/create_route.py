import json
import random

import googlemaps

from coords2dist import coords2dist


with open('keys.json', 'r') as file:
	KEY = json.loads(file.read())['google']['maps']['key']

with open('categories.json', 'r') as file:
	CATEGORIES = json.loads(file.read())

gmaps = googlemaps.Client(key=KEY)


def handler(emojis, time, geo):
	points = [{
		'geo': geo,
		'delta': 0,
	}]

	# Выборка эмодзи

	emojis = list(emojis)

	o = 0
	while len(emojis) > o:
		if emojis[o] not in CATEGORIES:
			del emojis[o]
		else:
			o += 1

	random.shuffle(emojis)

	# Время в расстояние

	# ! Учитывать время в каждой точке
	radius = 2.5 * time # m/min * min -> geo dist / count of places # 85 m/min

	#

	for emoji in emojis:
		# Ограничение, если слишком длинный путь

		if len(points) > 3:
			break

		# Преобразование в категории

		category = CATEGORIES[emoji]

		# Преобразование в места

		places = gmaps.places_nearby(
			location=(geo['lat'], geo['lng']),
			radius=radius,
			keyword = category,
		)['results']


		o = 0
		while len(places) > o:
			# Если уже было такое место

			for point in points:
				if places[o]['geometry']['location'] == point['geo']:
					del places[o]
					continue

			# Если место в обратной стороне

			if len(points) > 1 and (
				coords2dist(
					(
						points[-2]['geo']['lat'],
						points[-2]['geo']['lng']
					), (
						places[o]['geometry']['location']['lat'],
						places[o]['geometry']['location']['lng']
					)
				) <= coords2dist(
					(
						points[-1]['geo']['lat'],
						points[-1]['geo']['lng']
					), (
						places[o]['geometry']['location']['lat'],
						places[o]['geometry']['location']['lng']
					)
				)):
				del places[o]
				continue

			#

			if len(points) >= 1:
				t = False

				for point in points:
					delta = coords2dist(
						(
							point['geo']['lat'],
							point['geo']['lng']
						), (
							places[o]['geometry']['location']['lat'],
							places[o]['geometry']['location']['lng']
						)
					)

					# Если путь неоптимальный

					if delta <= point['delta']:
						t = True

					# Слишком близко

					if delta <= time * 1.5: # 90 m/min -> m/h
						t = True

				if t:
					del places[o]
					continue

			#

			o += 1

		# Если ни одного места

		if not len(places):
			continue

		# Выбор конкретного места

		place = places[random.randint(0, len(places)-1)]

		# Обновляем текущее местоположение

		geo = place['geometry']['location']

		# Обновляем дельты (для того, чтобы не идти обратно)

		for i in range(len(points)):
			points[i]['delta'] = coords2dist(
				(
					points[i]['geo']['lat'],
					points[i]['geo']['lng']
				), (
					place['geometry']['location']['lat'],
					place['geometry']['location']['lng']
				)
			)

		#

		points.append({
			'id': place['place_id'],
			'name': place['name'],
			'geo': place['geometry']['location'],
			'emoji': emoji,
			'delta': 0,
		})
	
	print(json.dumps(points, ensure_ascii=False, indent='\t'))

	return points[1:]


if __name__ == '__main__':
	print(handler('🍩🌃🍺🍽🛏', 180, {'lat': 47.390325, 'lng': 8.515934}))