#!/usr/bin/env python3

# package imports
import yaml

# verify that decode-config is available in PATH

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
