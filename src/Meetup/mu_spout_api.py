import requests
import json
import time
import sys
import os

from json import JSONDecoder
from functools import partial
import mu_mdb_client
from mu_mdb_client import mdb_insert
from mu_mdb_client import mdb_init


def mu_spout_start():

	mdb = mdb_init()

	# API Key from Meetup **** PLEASE KEEP CONFIDENTIAL ***
	api_key= "58677326234d7b421f64637b7564f5e"

	# Given a Country, State, City and Zip, get categories
	cities =[("New York","NY"),("San Francisco","CA"),("Miami","FL"),("Denver","CO"),("Los Angeles","CA"), ("Chicago","IL"),\
				("Houston", "TX"), ("Philadelphia", "PA"), ("Phoenix", "AZ"), ("San Antonio", "TX"), ("San Diego", "CA"), ("Houston", "TX")]

	# Data offset in Meetup response, start at 0, increment with every loop
	offset = 0

	# Need to explicitly force the API to return the "topics" and "category" fields
	fields=["topics,category"]

	# Run the main loop until stopped
	while True: 		
		for (city, state) in cities:

			#print("Processing {} : {} - Offset {}". format(city, state, offset))

			# Set up params for API call
			params = {"city":city, "state":state, "offset" : offset, "key":api_key, "fields":fields}

			# Call the Meetup API and get the results
			response=get_results(params)

			# Write out the retrieved data to a scratch file
			datafile = city.replace(" ", "_")+'_'+state+'_'+str(offset)+'_mu_data.json'
			outfile = open(datafile, 'w+') 
			#print(json.dumps(response, indent = 4, sort_keys=True))

			# Dump the received data to a scratchfile
			json.dump(response, outfile, indent=4, skipkeys = True, sort_keys = True, separators = (',', ':'))

			# Reset the pointer to the top of the file, to prepare to read
			outfile.seek(0)

			# Read the JSON from the scratchfile
			events = json.load(outfile)

			# Get the sub data that is more interesting
			events = events["results"]
			#print("\n\n\n\n\n\n\n\n\n\n\n")
			#print("PROCESSED EVENT IS:")
			#print(json.dumps(events, indent=4, sort_keys=True))

			# Write the data to the MongoDB database, one record at a time
			for event in events:
				#print(json.dumps(event, indent=4, sort_keys=True))
				mdb_insert(mdb, event)


			# Need to clean up the scratchfile. Locate it and delete it
			outfile.seek(0) 
			os.remove(datafile) 


		# Don't go too fast, for now. Meetup only allows 200 API calls per hour
		# that is 1 API call every 20 seconds. This is running 6 times that rate
		# but we'll see how not to get throttled
		time.sleep(20)

		# With the next API call, get the next set of data
		offset += 20


# Spawn the main process as a background task when the time comes. 
# Limited use for now
def mu_spout_on():
	import os
	os.spawnl(os.P_NOWAIT, mu_spout_start())


# Routine that gets the meetings data from Meetup.com 
def get_results(params):
	request = requests.get("https://api.meetup.com/2/open_events?&sign=true&country=us&&&radius=100&page=20",params=params)
	data = request.json()
	return data


if __name__=="__main__":
	mu_spout_start()




