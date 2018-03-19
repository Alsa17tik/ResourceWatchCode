FROM python:3.6
MAINTAINER Nathan Suberi <nathan.suberi@wri.org>

# install core libraries
RUN apt-get update
RUN pip install -U pip

# install application libraries
RUN apt-get install -y \
    cron \
    git-all

RUN apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        software-properties-common

# Is this necessary to spawn more containers?
# RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# set name
ARG NAME=swarm_manager
ENV NAME ${NAME}

# copy the application folder inside the container
WORKDIR /opt/$NAME/
COPY start.sh .

#RUN useradd -r $NAME
#RUN chown -R $NAME:$NAME /opt/$NAME
#VOLUME /opt/$NAME/data
#USER $NAME

CMD ["sh", "start.sh", "&&", "tail", "-f"]
