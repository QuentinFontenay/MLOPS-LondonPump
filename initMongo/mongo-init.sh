#!/bin/bash

echo "########### Loading data to Mongo DB ###########"
mongoimport --jsonArray --db london_fire --collection stations --file /tmp/data/stations.json
mongoimport --jsonArray --db london_fire --collection schoolVacations --file /tmp/data/schoolVacations.json
