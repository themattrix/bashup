FROM themattrix/tox

MAINTAINER Matthew Tardiff <mattrix@gmail.com>

ADD docker-scripts /docker-scripts
RUN chmod +x /docker-scripts/* \
    && mv /docker-scripts/* /usr/local/bin/ \
    && rm -rf /docker-scripts

ENV BASH_VERSIONS_DIR /bash
RUN mkdir $BASH_VERSIONS_DIR \
    && build-bash-versions 3.1 3.2 4.0 4.1 4.2 4.3
