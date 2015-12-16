# vim:set ft=dockerfile:
FROM birdhouse/bird-base:latest
MAINTAINER https://github.com/bird-house/pyramid-phoenix

LABEL Description="Phoenix WPS Application" Vendor="Birdhouse" Version="0.4.5"

# Configure hostname and user for services 
ENV HOSTNAME localhost
ENV USER www-data


# Set current home
ENV HOME /root

# Copy application sources
COPY . /opt/birdhouse

# cd into application
WORKDIR /opt/birdhouse

# Overwrite buildout.cfg in source folder
COPY minimal.cfg buildout.cfg

# Provide custom.cfg with settings for docker image
COPY .docker.cfg custom.cfg

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
EXPOSE 8081 8443

# Start supervisor in foreground
ENV DAEMON_OPTS --nodaemon --user $USER

# Start service ...
CMD ['make', 'update-config', 'start']

