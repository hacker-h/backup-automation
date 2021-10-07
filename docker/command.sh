#!/bin/sh
set -eu

# Setup GPG
for file_name in /srv/gpg_keys/*; do
    gpg --import ${file_name} 2> /tmp/gpg.output || cat /tmp/gpg.output
done
# Trust all private GPG keys ultimately
# https://raymii.org/s/articles/GPG_noninteractive_batch_sign_trust_and_send_gnupg_keys.html
for fpr in $(gpg --list-secret-keys --with-colons | awk -F: '/fpr:/ {print $10}' | sort -u); do
    echo -e "5\ny\n" |  gpg --batch --command-fd 0 --expert --edit-key ${fpr} trust 2> /tmp/gpg.output || cat /tmp/gpg.output;
done

gpg -K 2> /tmp/gpg.output | grep "unknown" || echo "All GPG keys trusted"

# Setup SSH
# TODO integrate automatically for all used hosts into backup.py
mkdir -p ~/.ssh
ssh-keyscan -t rsa github.com > ~/.ssh/known_hosts 2> /tmp/ssh.output || cat /tmp/ssh.output
ssh-keyscan -t rsa gitlab.com > ~/.ssh/known_hosts 2> /tmp/ssh.output || cat /tmp/ssh.output

while true; do
    python3.9 backup.py;
    sleep ${BACKUP_DELAY_IN_SECONDS};
done
