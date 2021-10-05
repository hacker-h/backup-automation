# Backup Automation
This is a tool to automatically backup your systems with encryption to storage backends.

# Features

- [x] Automatic backup fetching
    - [x] Tasmota Configurations
    - [ ] ZFS snapshots
    - [ ] linux directories via SSH
    - [ ] linux directories via [borg](https://www.borgbackup.org/)
- [x] Transparent encryption ([git-crypt](https://github.com/AGWA/git-crypt) + [gpg](https://gnupg.org/))
- [x] Backup differentially
- [x] Automatically upload to storage backend
    - [x] Git Backend
    - [ ] Nextcloud Backend
    - [ ] SSH Backend
- [x] Run as Python Script
- [ ] Run as (Docker) Container
- [ ] Container Image available on Docker Hub

# No Support planned
- ❌ HTTP(S) Git Repository backends

# Requirements
- at least one tasmota device with enabled web interface
- [Python 3.9](https://linuxize.com/post/how-to-install-python-3-9-on-ubuntu-20-04/) or newer
- [decode-config](https://github.com/tasmota/decode-config) available in PATH
- [git-crypt](https://github.com/AGWA/git-crypt) available in PATH
- [GPG](https://gnupg.org/) available in PATH

# Getting started
This will take only a few minutes.

## Storage backend
This is where your encrypted backups will be stored.

Currently only git backends are supported.
### Github as example
- Create a [new repository](https://github.com/new)
- Generate an SSH keypair without a password:
    ```
    ssh-keygen
    ```
    Remember where you store the two generated keys.
- Add the public key either as deploy key to your new repository or [globally to your account](https://github.com/settings/ssh/new).

## GPG Encryption key
You need a GPG key with encryption capabilities to encrypt your backup data.
### Create a dedicated GPG key for Encryption
For this purpose we will create a dedicated GPG key.

```
gpg --full-gen-key --expert
gpg (GnuPG) 2.2.19; Copyright (C) 2019 Free Software Foundation, Inc.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Please select what kind of key you want:
   (1) RSA and RSA (default)
   (2) DSA and Elgamal
   (3) DSA (sign only)
   (4) RSA (sign only)
   (7) DSA (set your own capabilities)
   (8) RSA (set your own capabilities)
   (9) ECC and ECC
  (10) ECC (sign only)
  (11) ECC (set your own capabilities)
  (13) Existing key
  (14) Existing key from card
Your selection? 8

Possible actions for a RSA key: Sign Certify Encrypt Authenticate 
Current allowed actions: Sign Certify Encrypt 

   (S) Toggle the sign capability
   (E) Toggle the encrypt capability
   (A) Toggle the authenticate capability
   (Q) Finished

Your selection? s

Possible actions for a RSA key: Sign Certify Encrypt Authenticate 
Current allowed actions: Certify Encrypt 

   (S) Toggle the sign capability
   (E) Toggle the encrypt capability
   (A) Toggle the authenticate capability
   (Q) Finished

Your selection? q
RSA keys may be between 1024 and 4096 bits long.
What keysize do you want? (3072) 4096
Requested keysize is 4096 bits
Please specify how long the key should be valid.
         0 = key does not expire
      <n>  = key expires in n days
      <n>w = key expires in n weeks
      <n>m = key expires in n months
      <n>y = key expires in n years
Key is valid for? (0) 0
Key does not expire at all
Is this correct? (y/N) y

GnuPG needs to construct a user ID to identify your key.

Real name: myBackupKey
Email address: 
Comment: 
You selected this USER-ID:
    "myBackupKey"

Change (N)ame, (C)omment, (E)mail or (O)kay/(Q)uit? O
We need to generate a lot of random bytes. It is a good idea to perform
some other action (type on the keyboard, move the mouse, utilize the
disks) during the prime generation; this gives the random number
generator a better chance to gain enough entropy.
gpg: key AA5678C075BD6E53 marked as ultimately trusted
gpg: revocation certificate stored as '/home/ubuntu/.gnupg/openpgp-revocs.d/6F354F058C89D54BC0AEB43CAA5678C075BD6E53.rev'
public and secret key created and signed.

pub   rsa4096 2021-10-04 [CE]
      6F354F058C89D54BC0AEB43CAA5678C075BD6E53
uid                      myBackupKey
```
In this example `6F354F058C89D54BC0AEB43CAA5678C075BD6E53` is your GPG User ID.
If you set a passphrase make sure to keep it save and backup your GPG key at a secure place (e.g. in your password manager or offline on an encrypted flash drive).

### Backup your GPG key
```bash
# make sure to adjust this before executing
GPG_LONG_ID=6F354F058C89D54BC0AEB43CAA5678C075BD6E53
# list your private key
gpg --list-secret-keys ${GPG_LONG_ID}
# export private key to file
gpg --armor --export-secret-keys ${GPG_LONG_ID} > ${GPG_LONG_ID}.gpg
# export the trust level of your owned keys
gpg --export-ownertrust > trustdb.txt
```

### Restore your GPG key from backup
```bash
# make sure to adjust this before executing
GPG_LONG_ID=6F354F058C89D54BC0AEB43CAA5678C075BD6E53

# delete your key in case you want to test backup restore in the same environment
# gpg --delete-secret-and-public-keys ${GPG_LONG_ID}
# import your key
gpg --import ${GPG_LONG_ID}.gpg

# delete your trustdb and import your trust backup,
# otherwise you will have to manually trust your key with gpg --edit-key ${GPG_LONG_ID}
rm ~/.gnupg/trustdb.gpg
gpg --import-ownertrust < trustdb.txt
# list your private key
gpg --list-secret-keys ${GPG_LONG_ID}
```


## Configuration
- make sure your gpg key is available:
  ```
  gpg --list-secret-keys
  ```
- fill out the `config.yaml.example` properly as `config.yaml`
- (optional) use the `secrets.yaml` to render variable values that start with `SECRET_`.

    This allows you to extract sensitive values from the `config.yaml`.

## Run with Python3.9
```
# (optional) create and use a virtualenv
virtualenv -p python3.9 ~/.venv/backup-automation
source ~/.venv/backup-automation/bin/activate

# install requirements
pip3.9 install -r requirements.txt
# run the backup script
python3.9 ./backup.py
```
