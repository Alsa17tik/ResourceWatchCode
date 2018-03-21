#!/bin/sh
NAME=easy_raster_upload
LOG=${LOG:-udp://localhost}

docker build -t $NAME --build-arg NAME=$NAME .
docker run \
    --log-driver=syslog --log-opt syslog-address=$LOG --log-opt tag=$NAME \
    --volume="$(pwd)"/rasters:/opt/$NAME/rasters \
    --env-file .env \
    --rm $NAME \
    python main.py
