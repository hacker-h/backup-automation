#!/usr/bin/env python3.9

# package imports
import sys
import shlex
import subprocess
import logging
import time
import yaml
from pprint import pprint
from shutil import which

# setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# constants
CONFIG_FILE = "config.yaml"
SECRETS_FILE = "secrets.yaml"
GIT_BACKEND = "git"
SECRET_PREFIX = "SECRET_"

# verify that decode-config is available in PATH
if which("decode-config") is not None:
    logger.debug("decode-config is available")
else:
    logger.error("decode-config is missing!")
    quit(1)

# parse yaml files
with open(CONFIG_FILE) as f:
    config_data = yaml.load(f, Loader=yaml.FullLoader)
with open(SECRETS_FILE) as f:
    secrets_data = yaml.load(f, Loader=yaml.FullLoader)

backends = config_data.get("backends")

templates = config_data.get("templates")

backup_configs = config_data.get("backup_configs")

secrets = secrets_data.get('secrets')

# validate yaml files data
# TODO

# render secrets into templates dict
for template_name in templates:
    template_entries = templates.get(template_name)
    key: str
    value: str
    for key, value in template_entries.items():
        if value.startswith(SECRET_PREFIX):
            secret_name = value.removeprefix(SECRET_PREFIX)
            secret_value = secrets.get(secret_name)
            template_entries[key] = secret_value

# render templates into backup_configs dict
for backup_config in backup_configs:
    template_name = backup_config.get("template", None)
    if template_name:
        template_entries = templates.get(template_name, None)
        if template_entries:
            backup_config={**backup_config, **template_entries}
            del backup_config["template"]
        else:
            logger.error("Invalid template_name '%s'", template_name)
            exit(1)

# setup backends

# iterate over backup configs

# fetch backup to tempdir

# encrypt backup to tempdir

# iterate over backends
# synchronize with backend
# pull latest backend git repo master branch

# copy encrypted backups to target directories in backends

# if git backend
# update backend git repo readme with current timestamp
# commit all changes

# push master branch

# if push fails, repeat: reset commit, stash, pull, stash pop, commit, push
