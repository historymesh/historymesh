#!/usr/bin/env bash

set -e

if [[ $# -eq 0 ]]; then
    echo "Usage: init_virtualenv.sh project [project..]"
    exit 1
fi

for project_name in $*; do
    env_name="$(basename $project_name)_ve"

    if [[ -e $env_name ]]; then
        if [[ -e $env_name/.init_ok ]]; then
            echo "Looks like you've already got a ${project_name} virtualenv here."
            echo "I'm not going to mess with it."
            exit 1
        else
            echo "Looks like your virtualenv didn't complete last time."
            echo "Blatting it."
            rm -rf $env_name
        fi
    fi

    echo "Setting up virtualenv for ${project_name}"
    virtualenv $env_name
    # Thanks to some weirdness with restkit/restpose/something, nose needs to
    # be installed first
    echo "Picking nose"
    pip install -E $env_name nose
    echo "Installing requirements"
    pip install -E $env_name -r ${project_name}/requirements.txt
    # Create a file to indicate the environment setup worked
    touch $env_name/.init_ok
done
