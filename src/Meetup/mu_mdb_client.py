import json
import pymongo
import pprint

from pymongo import MongoClient
from datetime import datetime
from config.mongo_config import *

#from testdata.json import testdata

# UNUSED ROUTINE. PLAN FOR FUTURE
# Parameters for Mongo DB instance and authentication.
# follow this with a auth_mdb_connect() call
# def setup_mdb_parameters():
# 	MONGO_HOST = MongoConfig.MONGO_HOST
# 	MONGO_USER= MongoConfig.MONGO_USER
# 	MONGO_PORT = MongoConfig.MONGO_PORT
# 	MONGO_DB = MongoConfig.DB_NAME
# 	MONGO_PASS = MongoConfig.MONGO_PASSWORD


# UNUSED ROUTINE. PLAN FOR FUTURE
# Connect to the MongoDB Server
# Returns a pointer to the database
# Use mdb_read and its variants to read records
def auth_mdb_connect():
	# point to the MOngoDB instance
	con=pymongo.mongo_client(MONGO_HOST,MONGO_PORT)

	# Once pointing to the instance, authenticate
	mdb=con[MONGO_DB]
	try:
		mdb.authenticate(MONGO_USER,MONGO_PASS)
	except:
		# Don;t print any error messages for now
		return None

	# return a pointer to the database
	return mdb


# Connect to the MongoDB Serer
#
# This sequence will connect to the MDB instance and reads can now be done
def setup_mdb_client():
	client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)

	# The database name is "meetup"
	try:
		client.meetup.authenticate(MONGO_USER, MONGO_PASSWORD)
	except:
		print(" ***** AUTHENTICATION WITH MONGO DB FAILED ***** ")

	# Stash a pointer to the database
	mdb = client[DB_NAME]

	# send the database pointer to the caller
	return mdb



# UNUSED ROUTINE
def mdb_init():
	mdb = setup_mdb_client()
	return mdb

# Use for inserting entries in MDB
def mdb_insert(mdb, data):
	result = mdb.meetup.insert_one(data)
	#print("DB Insertion SUCCESS - {}".format(result.inserted_id))


#result.inserted_id

#mdb_insert(mdb, data)


# Read many entries from the database
# Appears that Mongo db returns 20 entries by default. Have to double check
def mdb_read_many(mdb):

	# Get a cursor
	empCol = mdb.meetup.find()

	# keep count of processed entries
	count = 0

	# Iterate over the entries
	for entry in empCol:
		count += 1

		# print it out if necessary
		#print("\n\n\n\n\n\n")
		#pprint.pprint(entry)
		#print("\n\n\n")
		#print(json.dumps(entry, indent=4, sort_keys=True))
	print("Total entries : {}".format(count))


# Read only one entry from the Mongo DB server
def mdb_read_one(mdb):

	# Get a cursor
	empCol = mdb.meetup.find().limit(1)

	# Keep count of processed entries
	# There should be only one entry returned
	count = 0

	# The loop is unneeded, bacause only ony entry is returned
	# thanks to the limit(1) call
	for entry in empCol:
		count += 1

		#print(entry)

	# Use for debugging
	#print("Total entries : {}".format(count))

	# return the single entry
	return(entry)

# After testing, clean up the MongoDB database
# Used the testing routines mdb_test() and mdb_test_and_cleanup()
def mdb_cleanup(mdb):
	mdb.meetup.remove()

# FOR TESTING ONLY
# Setup cursor and Read
def mdb_test():
	mdb = setup_mdb_client()
	mdb_read_many(mdb)

# FOR TESTING ONLY
# Setup cursor, read and then cleanup
def mdb_test_and_cleanup():
	mdb = setup_mdb_client()
	mdb_read_many(mdb)
	mdb_cleanup(mdb)


if __name__ == "__main__":
	mdb_test_and_cleanup()
