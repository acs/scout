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
        && \
    apt-get clean && \
    find /var/lib/apt/lists -type f -delete

USER ${DEPLOY_USER}
WORKDIR ${DEPLOY_USER_DIR}

# get repository
RUN git clone https://github.com/acs/scout scout

USER root
# Configuring Apache
# RUN ${SCRIPTS_DIR}/configure-virtualhost.sh