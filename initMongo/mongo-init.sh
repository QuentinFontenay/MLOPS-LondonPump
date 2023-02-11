#!/bin/bash

echo "########### Loading data to Mongo DB ###########"
mongoimport --jsonArray --db london_fire --collection stations --file /tmp/data/stations.json
mongoimport --jsonArray --db london_fire --collection schoolVacations --file /tmp/data/schoolVacations.json
mongoimport --jsonArray --db london_fire --collection riskStations --file /tmp/data/riskStations.json

echo "########### Creating user ###########"
mongo -- "$MONGO_INITDB_DATABASE" <<EOF
    var rootUser = '$MONGO_INITDB_ROOT_USERNAME';
    var rootPassword = '$MONGO_INITDB_ROOT_PASSWORD';
    var admin = db.getSiblingDB('admin');
    admin.auth(rootUser, rootPassword);

    var user = '$MONGO_LONDON_FIRE_USER';
    var passwd = '$MONGO_LONDON_FIRE_PASSWORD';
    db.createUser({user: user, pwd: passwd, roles: ["dbOwner"]});
EOF
