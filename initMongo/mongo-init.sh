set -e
echo "########### Waiting for MongoDB to initialize ###########"
until mongo --host localhost --eval "print(\"waited for connection\")"
do
  sleep 1
done

echo "########### Check if database is already init ###########"
count=$(mongo --quiet -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --eval "db.riskStations.count()")
echo $count
if [ $count > 0 ]; then
    echo "Database is init"
    exit 2
fi

echo "########### Creating admin user ###########"
mongo <<EOF
    use admin;
    db.createUser({user: '$MONGO_INITDB_ROOT_USERNAME', pwd: '$MONGO_INITDB_ROOT_PASSWORD', roles: ["root"]});
EOF

echo "########### Loading data to Mongo DB ###########"
mongoimport --jsonArray --db london_fire --collection stations --authenticationDatabase admin --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD --file /tmp/data/stations.json
mongoimport --jsonArray --db london_fire --collection schoolVacations --authenticationDatabase admin --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD --file /tmp/data/schoolVacations.json
mongoimport --jsonArray --db london_fire --collection riskStations --authenticationDatabase admin --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD --file /tmp/data/riskStations.json

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
