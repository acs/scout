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
        python pep8 \
        apache2 \
        python-mysqldb python-requests \
        make \
        unzip wget \
        && \
    apt-get clean && \
    find /var/lib/apt/lists -type f -delete

# MySQL install and config and db creation
ADD configure-mysql.sh ${SCRIPTS_DIR}/configure-mysql.sh
# preseed debconf to set the mysql root password
RUN ${SCRIPTS_DIR}/configure-mysql.sh
RUN apt-get update && apt-get install -qy mysql-server

USER ${DEPLOY_USER}
WORKDIR ${DEPLOY_USER_DIR}

# Build web interface
RUN git clone https://github.com/VizGrimoire/VizGrimoireJS.git
RUN cd VizGrimoireJS && make && \
    cd .. && sudo ln -s ${DEPLOY_USER_DIR}/VizGrimoireJS events && \
    mkdir -p VizGrimoireJS/browser/data/json
# We need to update awesome for adding reddit icon
RUN cd VizGrimoireJS/browser/css && \
    mv awesome awesome.old && \
    wget http://fortawesome.github.io/Font-Awesome/assets/font-awesome-4.3.0.zip && \
    unzip font-awesome-4.3.0.zip && mv font-awesome-4.3.0 awesome

# get Scout repository
RUN git clone https://github.com/acs/scout scout

# Generate events and deploy them
RUN sudo service mysql start && \
    cd scout && make all && \
    cp scout.json ../VizGrimoireJS/browser/data/json/ && \
    cp html/browser/scout.html ../VizGrimoireJS/browser/index.html && \
    cp html/browser/lib/events.js ../VizGrimoireJS/browser/lib

USER root
RUN mv /var/www/html /var/www/html.orig
RUN ln -s ${DEPLOY_USER_DIR}/VizGrimoireJS/browser /var/www/html