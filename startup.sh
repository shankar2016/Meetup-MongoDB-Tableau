#! /bin/bash

mount -t ext4 /dev/xvdc /data
/root/start-hadoop.sh
/data/start_postgres.sh
sudo -u mongod mongod --dbpath /data/mongodb/  --fork --syslog
su - w205 -c '/data/start_metastore.sh'
cp -r . /home/w205/W205_Group_Project
chown -R w205:w205 /home/w205/W205_Group_Project
su - w205 -c 'PYTHONPATH=/home/w205/W205_Group_Project/src nohup python3 /home/w205/W205_Group_Project/src/Meetup/mu_start.py &'
sleep 120
su - w205 -c 'PYTHONPATH=/home/w205/W205_Group_Project/src spark-submit --jars /data/spark15/lib/mongo-hadoop-spark-2.0.1.jar --driver-class-path /data/spark15/lib/mongo-hadoop-spark-2.0.1.jar /home/w205/W205_Group_Project/src/spark/transform.py'
su - w205 -c 'hive --service hiveserver2 &'
