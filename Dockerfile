# vim:set ft=dockerfile:
FROM birdhouse/bird-base:latest
MAINTAINER https://github.com/bird-house/pyramid-phoenix

LABEL Description="Phoenix WPS Application" Vendor="Birdhouse" Version="0.4.5"

# Configure hostname and user for services 
ENV HOSTNAME localhost
ENV USER www-data
ENV OUTPUT_PORT 8090
ENV WPS_URL http://malleefowl:8091/wps
ENV PHOENIX_PASSWORD "sha256:10761810a2f2:8535bf8468e0045ec2d33bd4d2f513d669bd31b79794614f23632c3b2cadc51c"


# Set current home
ENV HOME /root

# Load sources from github
RUN mkdir -p /opt/birdhouse && curl -ksL https://github.com/bird-house/flyingpigeon/archive/master.tar.gz | tar -xzC /opt/birdhouse --strip-components=1

# cd into application
WORKDIR /opt/birdhouse

# Overwrite buildout.cfg in source folder
COPY minimal.cfg buildout.cfg

# Install system dependencies
RUN bash bootstrap.sh -i && bash requirements.sh

# Set conda enviroment
ENV ANACONDA_HOME /opt/conda
ENV CONDA_ENVS_DIR /opt/conda/envs

# Run install
RUN make clean install 

# Volume for data, cache, logfiles, ...
RUN chown -R $USER $CONDA_ENVS_DIR/birdhouse
RUN mv $CONDA_ENVS_DIR/birdhouse/var /data && ln -s /data $CONDA_ENVS_DIR/birdhouse/var
VOLUME /data/cache
VOLUME /data/lib

# Ports used in birdhouse
EXPOSE 8090 8081 8443

# Start supervisor in foreground
ENV DAEMON_OPTS --nodaemon --user $USER

# Update config and start supervisor ...
CMD ["make", "update-config", "start"]

