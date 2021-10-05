FROM python:3.9-alpine3.12@sha256:7f73901e568630443fc50e358b76603492e89c9bf330caf689e856a018f135f0 as builder

COPY ./requirements.txt /tmp/requirements.txt
RUN apk add gcc libffi-dev libressl-dev musl-dev &&\
    pip3 install --no-warn-script-location --user -r /tmp/requirements.txt &&\
    adduser -S backuper -s /bin/nologin -u 1537 &&\
    chown -R 1537 /root/.local

FROM python:3.9-alpine3.12@sha256:7f73901e568630443fc50e358b76603492e89c9bf330caf689e856a018f135f0 as runner

RUN apk add --no-cache gnupg openssh-client

RUN adduser -S backuper -s /bin/nologin -u 1537
USER 1537

COPY --from=builder /root/.local /home/backuper/.local
COPY ./backup.py /srv/
COPY ./docker/command.sh /srv/command.sh

WORKDIR /srv
CMD /srv/command.sh
