FROM ubuntu:latest
MAINTAINER Nathan Suberi <nathan.suberi@wri.org>

# install core libraries
RUN apt-get update

# install application libraries
RUN apt-get install -y \
    cron \
    git-all \
    docker \
    docker.io

# set name
ARG NAME=swarm_manager
ENV NAME ${NAME}

# copy the application folder inside the container
RUN mkdir -p /opt/$NAME
WORKDIR /opt/$NAME/

COPY entrypoint.sh .
COPY start.sh .
RUN chmod +x entrypoint.sh
RUN touch /var/log/cron

CMD ./entrypoint.sh && cron -l 7 && tail -f /var/log/cron
