# Imports
from data.db import load_db
import controller


# Load database
database = load_db()

# Maximum reviews
MAXIMUM_REVIEWS = 0
for place in database:
	reviews = "".join(database[place]['REVIEWS'].split(","))
	MAXIMUM_REVIEWS = max(MAXIMUM_REVIEWS, int(reviews))

# run controller
controller.controller(database, MAXIMUM_REVIEWS)