#!/usr/bin/env python3

# package imports
import sys
import shlex
import subprocess
import logging
import time
import yaml

# setup logging

# enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


# verify that decode-config is available in PATH
command = "which decode-config"
process= None
try:
    process = subprocess.Popen(shlex.split(command))
except:
    logger.error("ERROR %s while running %s" % (sys.exc_info()[1], command))

while True:
    return_code = process.poll()
    if return_code is not None:
        break
    time.sleep(0.2)
if return_code == 0:
    logger.info("decode-config is available")
else:
    logger.error("decode-config is missing!")
    quit(1)

# parse yaml files

# validate yaml files data

# setup backends

# clone or fetch git repository

# render secrets into templates dict

# render templates into backup_configs dict

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
