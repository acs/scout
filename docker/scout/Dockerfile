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
        npm nodejs nodejs-legacy \
        && \
    apt-get clean && \
    find /var/lib/apt/lists -type f -delete

# Google API lib for Python needed for accessing githubarchive bigdata API
RUN easy_install google-api-python-client && \
    chmod 644 /usr/local/lib/python2.7/dist-packages/httplib2-0.9.1-py2.7.egg/httplib2/cacerts.txt

# MySQL install and config and db creation
ADD configure-mysql.sh ${SCRIPTS_DIR}/configure-mysql.sh
# preseed debconf to set the mysql root password
RUN ${SCRIPTS_DIR}/configure-mysql.sh
RUN apt-get update && apt-get install -qy mysql-server

# jshint style for javascript code quality
RUN npm install -g jshint
# compiling angularjs app
RUN npm install -g bower

USER ${DEPLOY_USER}
WORKDIR ${DEPLOY_USER_DIR}

# get Scout repository
RUN git clone https://github.com/acs/scout scout

# Generate events and deploy them
RUN sudo service mysql start && \
    cd scout && make all

USER root
RUN mv /var/www/html /var/www/html.orig
RUN ln -s ${DEPLOY_USER_DIR}/app /var/www/html

# For testing with Protractor and PhantomJS
RUN apt-get update && \
    apt-get -y install --no-install-recommends \
    openjdk-7-jre \
    phantomjs

RUN npm -g install protractor && \
    webdriver-manager update

# Basic cleanup
RUN apt-get clean
