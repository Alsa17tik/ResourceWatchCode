FROM python:3.6
MAINTAINER Nathan Suberi <nathan.suberi@wri.org>
ARG NAME=easy_raster_upload
ENV NAME ${NAME}

# install core libraries
RUN apt-get update
RUN pip install -U pip

# install application libraries
RUN pip install -e git+https://github.com/fgassert/eeUtil#egg=eeUtil

# copy the application folder inside the container
RUN mkdir -p /opt/$NAME/rasters
WORKDIR /opt/$NAME/
COPY contents/ .
VOLUME /opt/$NAME/rasters

RUN groupadd -r $NAME && useradd -r -g $NAME $NAME
RUN chown -R $NAME:$NAME /opt/$NAME/
USER $NAME

# Launch script
CMD ["python", "main.py"]
