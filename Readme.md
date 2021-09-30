# Backup Automation
This is a tool to automatically backup your systems with encryption to storage backends.

## Requirements
```
sudo wget -O /usr/local/bin/decode-config https://github.com/tasmota/decode-config/releases/download/v9.5.0/decode-config_linux
sudo chmod +x /usr/local/bin/decode-config
```

Setup `config.yaml` and `secrets.yaml` according to the `.example` files.

## Features

- [x] Automatic backup fetching
    - [x] Tasmota Configurations
    - [ ] ZFS snapshots
    - [ ] linux directories via SSH
    - [ ] linux directories via [borg](https://www.borgbackup.org/)
- [ ] Transparent encryption
- [ ] Backup differentially
- [ ] Automatically upload to storage backend
    - [ ] Git Backend
    - [ ] Nextcloud Backend
    - [ ] SSH Backend
- [ ] Run as Python Script
- [ ] Run as (Docker) Container
- [ ] Container Image available on Docker Hub

## No Support planned
- ❌ HTTP(S) Git Repository backends

## Requirements
- at least one tasmota device with enabled web interface
- fill out the `config.yaml.example` properly as `config.yaml`
- (optional) use the `secrets.yaml` to render variable values that start with `SECRET_`.

## Getting started
