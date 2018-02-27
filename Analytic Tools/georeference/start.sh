#!/bin/sh

#Change the NAME variable with the name of your script
NAME=georeference

docker build -t $NAME --build-arg NAME=$NAME .
docker run \
    --volume="$(pwd)"/data:/opt/$NAME/data \
    --env-file .env \
    --rm $NAME \
    python main.py
#--net="host" \
# --log-driver=syslog --log-opt syslog-address=$LOG --log-opt tag=$NAME
