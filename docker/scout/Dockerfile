# Copyright (C) 2015 Bitergia
# GPLv3 License

FROM bitergia/ubuntu-trusty:latest
MAINTAINER Alvaro del Castillo <acs@bitergia.com>

ENV DEBIAN_FRONTEND noninteractive
ENV DEPLOY_USER bitergia
ENV DEPLOY_USER_DIR /home/${DEPLOY_USER}
ENV SCRIPTS_DIR ${DEPLOY_USER_DIR}/scripts

# Helper scripts
RUN mkdir ${DEPLOY_USER_DIR}/scripts

# install dependencies
RUN apt-get update && \
    apt-get -y install --no-install-recommends \
        bash \
        git git-core \
        tree ccze \
        psmisc \
        python \
        apache2 \
        python-mysqldb\
        make \
        && \
    apt-get clean && \
    find /var/lib/apt/lists -type f -delete

USER ${DEPLOY_USER}
WORKDIR ${DEPLOY_USER_DIR}

# get repository
RUN git clone https://github.com/acs/scout scout
RUN cd scout && git clone https://github.com/VizGrimoire/GrimoireLib.git && ln -s GrimoireLib/vizgrimoire
USER root
# Just for GrimoireLib
RUN apt-get update && apt-get -y install --no-install-recommends \
        python-dateutil python-rpy2
RUN apt-get -y install --no-install-recommends \
        python-scipy

# MySQL install and config and db creation
ADD configure-mysql.sh ${SCRIPTS_DIR}/configure-mysql.sh
# preseed debconf to set the mysql root password
RUN ${SCRIPTS_DIR}/configure-mysql.sh
RUN apt-get update && apt-get install -qy mysql-server
RUN service mysql start

USER ${DEPLOY_USER}
# Build web interface
RUN git clone https://github.com/VizGrimoire/VizGrimoireJS.git
RUN cd VizGrimoireJS && make && \
    cd .. && sudo ln -s ${DEPLOY_USER_DIR}/VizGrimoireJS events && \
    mkdir -p VizGrimoireJS/browser/data/json && \
    cp scout/html/browser/scout.html VizGrimoireJS/browser/index.html && \
    cp scout/html/browser/lib/events.js VizGrimoireJS/browser/lib

# Generate events and deploy them
RUN cd scout && make events && \
    cp scout.json ../VizGrimoireJS/browser/data/json/

USER root