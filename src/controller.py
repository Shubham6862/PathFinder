# Imports
from heapq import heappush, heappop
from haversine import haversine
from math import exp
from user.requirements import user_requirement
from data.db import search
from algorithm.path import best_route
from algorithm.scheduler import schedule
from algorithm.collaborative import RecommentedPlaces as recommended_places
import csv

NO_OF_PLACES_PER_DAY = 5

def controller(
		database,		# Dict
		MAXIMUM_REVIEWS	# Int
	):
	# Get user requirements
	places, starts_at, ends_at, total_days, total_budget, user_id, include_visited_places = user_requirement()

	# Search places
	# lookup_fields = ['DISTRICT']
	# search_results = search(database, lookup_fields, places)
	dframe = recommended_places(places, user_id, total_days * NO_OF_PLACES_PER_DAY, include_visited_places)

	search_results = list(dframe.title)
	item_ids = list(dframe.itemId)

	# Sort places according to rating
	heap = sort_places_by_rating_review(search_results, database, MAXIMUM_REVIEWS)

	# Till the schedule fits
	while True:
		# Get all the remaining places
		remaining_places = []
		for rating, place in heap:
			remaining_places.append(place)

		# Create matrix and mapping
		matrix, mapping = create_matrix_and_mapping(database, remaining_places)

		# Create route
		head = best_route(matrix, len(remaining_places))

		# Get place visit order
		place_visit_order = []
		while head:
			index = head.val
			place_visit_order.append(remaining_places[index])
			head = head.next
		
		# Generate schedule
		possible, time_table = schedule(matrix, mapping, database, place_visit_order, total_days, starts_at, ends_at, total_budget)

		# If schedule fits
		if possible:
			# Disply the schedule
			print()
			for index, each_day in enumerate(time_table):
				print('-' * 15, 'DAY', index + 1, '-' * 15)
				for each_place in each_day:
					print(each_place)
				print("\n")

			print("\nYOUR FEEDBACK\n")

			with open(r"C:\Users\sanja\Downloads\trip\Travel-Planner-master\src\data1\Myn_data.csv", 'a') as f:
				writer = csv.writer(f)
				for place in place_visit_order:
					index = search_results.index(place)
					item_id = item_ids[index]
					writer.writerow([user_id, item_id, float(input(place + ' rating: '))])

			# Stop
			break

		# Else remove the place with the least rating
		heappop(heap)


def create_matrix_and_mapping(
		database,	# Dict
		places		# List[str]
	):
	# Initialize matrix and mapping
	length = len(places)
	matrix = [[0 for __ in range(length)] for _ in range(length)]
	mapping = {}
	# Construct matrix
	for i in range(length):
		# Create point A
		place_a = places[i]
		point_a = (
			float(database[place_a]['COORDINATES']['LATITUDE']),
			float(database[place_a]['COORDINATES']['LONGITUDE'])
		)
		# Create mapping
		mapping[place_a] = i
		for j in range(i + 1, length):
			# Create point B
			place_b = places[j]
			point_b = (
				float(database[place_b]['COORDINATES']['LATITUDE']),
				float(database[place_b]['COORDINATES']['LONGITUDE'])
			)
			# Compute distance
			distance = haversine(point_a, point_b)
			matrix[i][j] = matrix[j][i] = distance
	return matrix, mapping


def weighted_rating(
		rating,			# Float
		reviews, 		# Int
		MAXIMUM_REVIEWS	# Int
	):
	reviews = int("".join(reviews.split(",")))
	return (1/(1+exp((-reviews*10)/MAXIMUM_REVIEWS)))*rating


def sort_places_by_rating_review(
		places,			# List[Str]
		database,		# Dict
		MAXIMUM_REVIEWS	# Int
	):
	# Initialize heap
	heap = []

	# Sort places according to rating
	for place in places:
		rating = float(database[place]['RATING'])
		reviews = database[place]['REVIEWS']
		weight_rating_value = weighted_rating(rating, reviews, MAXIMUM_REVIEWS)
		heappush(heap, (weight_rating_value, place))

	return heap