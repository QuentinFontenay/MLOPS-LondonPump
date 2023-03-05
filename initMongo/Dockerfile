FROM mongo:5.0.5
COPY initMongo/data/ /tmp/data
COPY initMongo/mongo-init.sh /docker-entrypoint-initdb.d
RUN chmod +x /docker-entrypoint-initdb.d/mongo-init.sh
CMD ["/bin/sh" , "-c", "mongod --auth --dbpath=/dbdata --bind_ip 0.0.0.0 & ./docker-entrypoint-initdb.d/mongo-init.sh & wait"]
