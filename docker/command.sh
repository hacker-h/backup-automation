#!/bin/sh
# setup gpg
gpg --import-ownertrust < /srv/trustdb.txt
for file_name in /srv/gpg_keys/*; do
    gpg --import ${file_name}
done

# setup ssh
# TODO integrate automatically for all used hosts into backup.py
mkdir -p ~/.ssh
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts
ssh-keyscan -t rsa gitlab.com >> ~/.ssh/known_hosts

while true; do
    python3.9 backup.py;
    sleep ${BACKUP_DELAY_IN_SECONDS};
done
