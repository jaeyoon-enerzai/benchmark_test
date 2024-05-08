FROM alpine:3.18 AS base

WORKDIR /workspace

RUN apk add \
        apache2 \
        apache2-mod-wsgi \
        apache2-utils apache2-dev \
        python3-dev \
        py3-pip 
RUN apk add --no-cache bash
RUN adduser -D -H webuser webuser
RUN apk add build-base

COPY requirements.txt /workspace/requirements.txt
RUN python3 -m venv venv && \
    source venv/bin/activate && \
    pip install -r /workspace/requirements.txt


COPY --chown=webuser:webuser wsgi.py /workspace/wsgi.py
COPY apache2.conf /etc/apache2/conf.d/benchmark.conf
COPY testrun.sh /workspace/testrun.sh

# 풀기
# COPY benchmark /workspace/benchmark

# CMD ["/usr/sbin/httpd", "-k", "start", "-e", "info", "-D", "FOREGROUND"]
CMD ["./testrun.sh"]
EXPOSE 5000