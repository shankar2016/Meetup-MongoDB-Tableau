This directory contains code to invoke and run the meetup open events API.
This API searches for recent and upcoming public events hosted by Meetup groups.
Its search window is the past one month through the next three months. Open Events
searches for current events by location, category, topic, or text, and only lists
Meetups that have 3 or more RSVPs.



To programmatically run this API and get a stream of data
=========================================================
BEFORE STARTING:  These scripts use a common mongo_config.py file containing mongo configuration
To ensure that this config file is available to be included, the following command must be run:
	$ export PYTHONPATH=<path/to/repository>/src

1). Follow the code in mu_start.py
	- Use the 3 import statements
	- call the mu_spout_on() function

THis call will generate a open events stream from 6 chosen cities with the call running
in an endless loop. The call between APIs is time delayed by 20 seconds so that we do not
exceeed the 200 API calls per hour.


To run the program from console
==============================
1). Option 1. Call the mu_spout_on() function by:
	- python3 mu_start.py

2). Run the mu_spout_on funtion directly by
	- python3 mu_spout_api.py


To clean up MongoDB after any testing, use the mu_mdb_client.py
===============================================================

- python3 mu_mdb_client.py

THIS CALL WILL DELETE ALL STORED ENTIES IN THE MONGODB. USE WITH CAUTION.
