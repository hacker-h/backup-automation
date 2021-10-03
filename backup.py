#!/usr/bin/env python3.9

# package imports
from datetime import datetime
import json
import requests
import sys
import shlex
import subprocess
import logging
import time
import yaml
import os
from pprint import pprint
from shutil import which
import shutil
import git
import pathlib
from pathlib import Path

# setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger("backup")

# constants
CONFIG_FILE = "config.yaml"
SECRETS_FILE = "secrets.yaml"
GIT_BACKEND = "git"
SECRET_PREFIX = "SECRET_"
TEMP_DIR = "/tmp/.backup-automation"
GIT_ATTRIBUTES_CONTENT = """
*              filter=git-crypt diff=git-crypt
.gitattributes !filter !diff !merge text
.gitignore     !filter !diff !merge text
README.md      !filter !diff !merge text
"""
# verify that decode-config is available in PATH
if which("decode-config") is not None:
    logger.debug("decode-config is available")
else:
    logger.error("decode-config is missing!")
    quit(1)
# verify that git-crypt is available in PATH
if which("git-crypt") is not None:
    logger.debug("git-crypt is available")
else:
    logger.error("git-crypt is missing!")
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
rendered_backup_configs = []
for backup_config in backup_configs:
    template_name = backup_config.get("template", None)
    if template_name:
        template_entries = templates.get(template_name, None)
        if template_entries:
            del backup_config["template"]
            new_backup_config = {**backup_config, **template_entries}
            rendered_backup_configs.append(new_backup_config)
        else:
            logger.error("Invalid template_name '%s'", template_name)
            exit(1)

backup_configs = rendered_backup_configs

# setup backends
for backend_name in backends:
    backend = backends[backend_name]
    backend_type = backend.get("type")
    if backend_type == GIT_BACKEND:
        # clone or update git repository
        repo_url: str = backend.get("repository_url")
        repo_dir: str = backend.get("repository_directory")
        identity_file: str = backend.get("identity_file")
        ssh_cmd = "ssh -i %s" % identity_file
        Path(repo_dir).mkdir(parents=True, exist_ok=True)
        git_repo = git.Repo.init(repo_dir)
        try:
            remote = git_repo.remote("origin")
            if remote.url != repo_url:
                # delete invalid remote
                git_repo.delete_remote("origin")
                logger.error("origin pointed to wrong remote URL '%s', expected '%s'. Fixing..",
                             remote.url, repo_url)
                raise ValueError(
                    "Wrong remote URL, remote has to be recreated")
        except ValueError:
            logger.info("adding new remote origin")
            remote = git_repo.create_remote("origin", repo_url)
        # fetch upstream branches
        # remote.fetch()
        # remote.update()
        remote_is_empty = False
        with git_repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
            try:
                logger.info("pulling remote master branch")
                remote.pull("master")
            except git.exc.GitCommandError as e:
                if "couldn't find remote ref master" in e.stderr:
                    logger.info("remote master branch is missing")
                    remote_is_empty = True
                    if "master" in git_repo.heads:
                        logger.debug("local master branch exists")
                        git_repo.git.checkout("master")
                    else:
                        logger.info("creating local master branch")
                        git_repo.git.checkout(b="master")
                elif "Could not read from remote repository" in e.stderr:
                    logger.error("repository does not exist or is not readable")
                    exit(1)
                else:
                    raise e
        untracked_files = git_repo.untracked_files
        if untracked_files:
            logger.error("There are untracked files in repo '%s'", repo_dir)
            exit(1)
        git_attributes_path = os.path.join(repo_dir, ".gitattributes")
        if Path(git_attributes_path).is_file():
            logger.debug(".gitattributes already exists")
        else:
            logger.info(".gitattributes is missing")
            logger.info("creating .gitattributes")
            with open(git_attributes_path, "w+") as f:
                f.write(GIT_ATTRIBUTES_CONTENT)
            pass
            logger.info("there are untracked files")
            git_repo.index.add(untracked_files)
            git_repo.index.commit("add .gitattributes")
        # TODO enable git-crypt
        command = "git-crypt init"
        try:
            process_handle = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            process_output = process_handle.stdout.decode()
            if "already been initialized" in process_output:
                logger.debug("git-crypt is already initialized")
            elif "Generating key..." in process_output:
                logger.debug("git-crypt initialized")
        except:
            logger.error("{} while running {}".format(
                sys.exc_info()[1], command))
            exit(1)
        # TODO export + import key functionality
        
        num_local_commits = len(list(git_repo.iter_commits("master")))
        logger.debug("num_local_commits: '%i'", num_local_commits)
        num_remote_commits = len(list(git_repo.iter_commits("origin/master")))
        if remote_is_empty:
            num_remote_commits = 0
        logger.debug("num_remote_commits: '%i'", num_remote_commits)
        unpushed_commits = num_local_commits > num_remote_commits
        if unpushed_commits:
            with git_repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
                logger.info("pushing master")
                remote.push("master")
        else:
            logger.debug("there are no unpushed commits")
        exit(0)
    else:
        logger.error("Unsupported backend_type '%s'", backend_type)
        exit(1)
# create tempdir
try:
    os.mkdir(TEMP_DIR)
except FileExistsError:
    pass

# iterate over backup configs
for backup_config in backup_configs:
    # TODO handle empty + omitted fields
    backend_name: str = backup_config.get("backend_name")
    backup_host: str = backup_config.get("host")
    http_password = backup_config.get("http_password")
    http_username = backup_config.get("http_username")
    repository_sub_directory = backup_config.get("repository_sub_directory")

    # fetch binary backup to tempdir
    backup_download_url = "http://%s/dl" % backup_host
    try:
        logger.info("Fetching backup for '%s'", backup_host)
        response = requests.get(backup_download_url,
                                auth=(http_username, http_password))
    except OSError:
        logger.error("Skipping '%s': network error", backup_host)
        continue
    temp_dmp_name = "%s.dmp" % backup_host.replace("/", "_")
    temp_dmp_path = os.path.join(TEMP_DIR, temp_dmp_name)
    with open(temp_dmp_path, "wb") as f:
        f.write(response.content)

    # decode binary to json
    command = "decode-config -s %s" % temp_dmp_path
    temp_json_name = "%s.json" % backup_host.replace("/", "_")
    temp_json_path = os.path.join(TEMP_DIR, temp_json_name)
    with open(temp_json_path, "w+") as f:
        try:
            process_handle = subprocess.call(shlex.split(command), stdout=f)
        except:
            logger.error("{} while running {}".format(
                sys.exc_info()[1], command))
            exit(1)

        # try to parse the obtained json
        f.seek(0)
        json_content = f.read()
        try:
            json_dict = json.loads(json_content)
        except json.decoder.JSONDecodeError:
            logger.error("Invalid JSON data from host '%s'", backup_host)
            exit(1)
    # remove temporary dmp file
    os.remove(temp_dmp_path)

    # store new backup to backend
    backend = backends[backend_name]
    backend_type = backend.get("type")
    if backend_type == GIT_BACKEND:
        repo_path = backend.get("repository_directory")
        sub_directory = backup_config.get("repository_sub_directory")
        repo_sub_path = os.path.join(repo_path, sub_directory)
        # make sure sub directory exists
        Path(repo_sub_path).mkdir(parents=True, exist_ok=True)
        repo_file_path = os.path.join(repo_sub_path, temp_json_name)
        # move json to backend repo
        shutil.move(temp_json_path, repo_file_path)

# timestamp commit message
now = datetime.now()  # current date and time
commit_message = now.strftime("%Y-%m-%d %H:%M:%S update backups")

# iterate over backends
for backend_name in backends:
    backend = backends[backend_name]
    backend_type = backend.get("type")
    if backend_type == GIT_BACKEND:
        repo_url: str = backend.get("repository_url")
        repo_dir: str = backend.get("repository_directory")
        identity_file: str = backend.get("identity_file")
        ssh_cmd = "ssh -i %s" % identity_file
        remote = git_repo.remote("origin")
        # pull upstream changes
        with git_repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
            remote.pull("master")
        untracked_files = git_repo.untracked_files
        if untracked_files:
            logger.info("There are untracked files: '%s'", untracked_files)
            git_repo.index.add(untracked_files)
            logger.info("Committing")
            git_repo.index.commit(commit_message)
            logger.info("Commit created")
            with git_repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
                remote.push("master")
    else:
        logger.error("Unsupported backend_type '%s'", backend_type)
        exit(1)

# TODO
# if push fails, repeat: reset commit, stash, pull, stash pop, commit, push
