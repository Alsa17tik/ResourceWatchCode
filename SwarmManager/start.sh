#!/bin/bash

NAME=swarm_manager
LOG=${LOG:-udp://localhost}

docker build -t $NAME --build-arg NAME=$NAME .
docker run --log-driver=syslog \
           --log-opt syslog-address=$LOG \
           --log-opt tag=$NAME \
           -v $(pwd)/data:/opt/$NAME/data \
           -v /var/run/docker.sock:/var/run/docker.sock \
           --env-file .env \
           --rm $NAME 
