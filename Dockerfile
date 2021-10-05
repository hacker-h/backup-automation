FROM python:3.9-alpine3.12@sha256:7f73901e568630443fc50e358b76603492e89c9bf330caf689e856a018f135f0 as builder

COPY ./requirements.txt /tmp/requirements.txt
RUN apk add gcc libffi-dev libressl-dev musl-dev &&\
    pip3 install --no-warn-script-location --user -r /tmp/requirements.txt &&\
    adduser -S backuper -s /bin/nologin -u 1537 &&\
    chown -R 1537 /root/.local

FROM python:3.9-alpine3.12@sha256:7f73901e568630443fc50e358b76603492e89c9bf330caf689e856a018f135f0 as runner

RUN apk add --no-cache git git-crypt gnupg openssh-client
ENV DECODE_CONFIG_VERSION="v9.5.0"
RUN wget -O /usr/local/bin/decode-config \
    "https://raw.githubusercontent.com/tasmota/decode-config/${DECODE_CONFIG_VERSION}/decode-config.py" &&\
    chmod +x /usr/local/bin/decode-config

RUN adduser -S backuper -s /bin/nologin -u 1537

RUN chown -R 1537 /srv
USER 1537

COPY --from=builder /root/.local /home/backuper/.local
COPY ./backup.py /srv/
COPY ./docker/command.sh /srv/command.sh

WORKDIR /srv
CMD /srv/command.sh
