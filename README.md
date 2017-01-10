# W205_Group_Project
Repository for W205-4 fall class project with Karin, Dan, Shankar and Chandler.

## Goals / Why Meetup
The goal of our project is to measure public sentiment and interests by examining the topics of Meetup events across the United States.  Our choice of Meetup as a data source is due to the diversity of locales that Meetup events occur in, offering a sample of data that can target less populous areas rather than just major cities.  Data from Meetup will allow us to identify frequent event themes across many locations, and anticipate up and coming trends by looking at Meetups that are scheduled in the advance.

# Running the code
An AMI has been built specifically to run this project named MIDS_Fall_W205-4_Meetup, start an EC2 instance using this image and open port 10000 on it if you wish to be able to connect Tableau to the Hive serving layer.

## Running using the startup script
After launching the instance and using ssh to connect to it as root, run the following commmands to run the end to end code:
```
git clone git@github.com:cmccann11/W205_Group_Project.git
cd W205_Group_Project
./startup.sh
```

## Running the pieces of the code individually
This code is intended to be run as the w205 user on the provided EC2 instance.  If you've already run the startup script, then the code will be present in the w205 home directory.  If not it should be copied/cloned to be made available to the w205 user.

### Meetup data collection
The code for the Meetup data collection is located in `src/Meetup/`.  This directory contains code to invoke and run the Meetup open events API.  This API searches for recent and upcoming public events hosted by Meetup groups.  Its search window is the past one month through the next three months. Open Events searches for current events by location, category, topic, or text, and only lists Meetups that have 3 or more RSVPs.

BEFORE STARTING:  These scripts use a common mongo_config.py file containing mongo configuration.
To ensure that this config file is available to be included, the following command must be run:
```
export PYTHONPATH=<path/to/repository>/src
```
Note this command only needs to be run once per session.

#### Using python interpreter
```
$ export PYTHONPATH=<path/to/repository>/src
$ cd src/Meetup
$ python3
>>> import mu_spout_api
>>> from mu_spout_api import mu_spout_on
>>> import mu_mdb_client
>>> mu_spout_on()
```

This call will generate a open events stream from 6 chosen cities with the call running
in an endless loop. The call between APIs is time delayed by 20 seconds so that we do not
exceeed the 200 API calls per hour.


#### To run the program from console
1). Option 1. Call the mu_spout_on() function by:
  ```
  export PYTHONPATH=<path/to/repository>/src
  python3 mu_start.py
  ```
2). Run the mu_spout_on funtion directly by
  ```
  export PYTHONPATH=<path/to/repository>/src
  python3 mu_spout_api.py
  ```

#### To clean up MongoDB after any testing, use the mu_mdb_client.py
  ```
  export PYTHONPATH=<path/to/repository>/src
  python3 mu_mdb_client.py
  ```
THIS CALL WILL DELETE ALL STORED ENTRIES IN THE MONGODB. USE WITH CAUTION.

### Meetup data transformation
The meetup data transformation and creating of the serving layer is handled using spark.  The code located in `src/spark`.  The code will read that data in from the Mongo data store, clean and store the data in Hive where it can be served up to other applications.

#### To run from the console
```
export PYTHONPATH=<path/to/repository>/src
cd src/spark
spark-submit --jars /data/spark15/lib/mongo-hadoop-spark-2.0.1.jar \
  --driver-class-path /data/spark15/lib/mongo-hadoop-spark-2.0.1.jar \
  transform.py
```

# Dependencies

## Meetup data collection Dependencies
The Meetup data collection pipeline is designed to be run with python 3, and requires the `pymongo` and `requests` python modules to available.  Additionally there must be a MongoDB server available, the connection info for this MongoDB can be configured in `src/config/mongo_config.py`.

Requirements:
- python 3
- pymongo python package
- requests python package
- MongoDB server

## Data transformation Dependencies
The data transformation must be run on spark, and it built targeting spark 1.5.  In addition to spark, the data will be stored in Hive, and a server will need to be set up running hadoop/hive and spark will need to be configured to connect with it.  Finally, some additional python modules and spark libraries for spark are required for spark to connect to mongo.  Python requires the `pymongo` module, which can be installed using pip, and the `pymongo_spark` module, which is included in this codebase.  The mongo-hadoop-spark libraries are required for spark, and need to be included in the spark path when submitting the job, as shown in the spark-submit command above.  The required libraries can be build from the source: https://github.com/mongodb/mongo-hadoop.  Once built the required jar file will be located in `spark/build/libs`.

Requirements:
- Hadoop and Hive
- Spark 1.5 configured to connect to Hive metastore
- python 2
- mongo-hadoop-spark library https://github.com/mongodb/mongo-hadoop
- pymongo python package
- pymongo_spark python package (included)

# Architecture

## Configuration
Configuration files are located under `src/config`.  This contains the shared configurations for the individual portions of the pipeline.

The config directory contains the following file:
  - mongo_config.py: This file contains the mongo db connection info, by default configured to use localhost, but allows us to easily switch to a dedicated remote mongo server if required.

## Meetup data collection
Our data collection script consists of a python program which will connect to the Meetup API.  The script will read in 20 additional events every 20 seconds and inserts the results into the Mongo DB.

This program consists of to following files:
  - mu_mdb_client.py: This script handles communication with the Mongo DB including inserting new documents, and if required, cleanup of the collection.
  - mu_spout_api.py: This script handles gathering data from the Meetup API and utilizes the mu_mdb_client to insert the gathered events into Mongo DB
  - mu_start.py: A start up script that launches the data collection program.

## Mongo data store
The technology chosen for our data store is MongoDB.  Mongo is well suited for this task as documents are stored in Mongo in a JSON like format and the data coming in from Meetup is already in JSON.  This allows us to store our data and its schema easily and with minimal preprocessing.  Usage of Mongo offers us the ability to use a self hosted solution, compared an option like S3, but is still an option that is easy to scale horizontally as our data volume grows.

## Spark data transformation
Our data transformations are done using spark.  To connect to mongo, it requires some additional libraries which are covered in the dependencies section.  The transformation portion of the pipeline is located in `src/spark`:

  - transform.py - our data transformation script.  This script can pull data out of mongo, parallelizing it into multiple RDDs if required, extracts the desired fields that we want for analysis and persists it to our serving layer in Hive.

## Hive serving layer
Hive is our choice as the persistent storage for our serving layer.  Hive provides good integration support with both Spark and Tableau.  Spark RDDs can be easily stored in Hive, which simplifies our data manipulation in Spark.  One alternative considered was to server the Spark RDDs directly through ThriftServer, however at this time it does not seem that the python Spark libraries support this option.  This is supported in Scala, and a potential future work item could be to convert our data transformation code to Scala to utilize this option.  HBase was also considered, however direct connection from Tableau to HBase is not possible, instead a Hive table must be created that maps to the HBase table.  This lead us to using Hive which is a known compatable option with both pyspark and Tableau.

## Tableau Visualization
Tableau is our visualization tool of choice.  With a low learning curve, it was easy for us to get it up and running with a few sample visualizations demonstrating the analysis that can be done with our data set.  These visualizations are located in the Tableau directory.

Our project includes these visualizations:
  - Meetup_love.twbx: From Meetup With Love - allows you to discover locations in the US where you might find the highest concentration of potential partners that are compatible with you based on your interests.  See it in action here: https://public.tableau.com/profile/dan.watson#!/vizhome/Meetup_love/MeetupWLove
  - w205_book.twb: Find your Niche - Discover potential markets based on interest categories.  Available to try out here: https://public.tableau.com/profile/dan.watson#!/vizhome/w205_book/MarketingDashboard
  - w205_Story.twb: Find a new location - Explore and drill down into the data, discovering areas in the United States that have others with interests and availability similar to yours.  See it here: https://public.tableau.com/profile/dan.watson#!/vizhome/Meetup_Story/Story1
