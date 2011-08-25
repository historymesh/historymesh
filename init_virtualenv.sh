#!/usr/bin/env bash

set -e

if [[ $# -eq 0 ]]; then
    echo "Usage: init_virtualenv.sh project [project..]"
    exit 1
fi

for project_name in $*; do
    env_name="$(basename $project_name)_ve"

    if [[ -e $env_name ]]; then
    echo "Looks like you've already got a ${project_name} virtualenv here."
    echo "I'm not going to mess with it."
    exit 1
    fi

    echo "Setting up virtualenv for ${project_name}"
    virtualenv $env_name
    # Thanks to some weirdness with restkit/restpose/something, nose needs to
    # be installed first
    echo "Picking nose"
    pip install -E $env_name -i http://pypi.fort/ nose
    echo "Installing requirements"
    pip install -E $env_name -i http://pypi.fort/ -r ${project_name}/requirements.txt
done
