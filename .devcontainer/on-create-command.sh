#!/usr/bin/env bash
set -e

# Install add-apt-repository
sudo apt update && sudo apt install -y software-properties-common

# Add the deadsnakes ppa for Python 3.7 and Python 3.9
# https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa
sudo add-apt-repository -y ppa:deadsnakes/ppa

# Install Python 3.7 and 3.9
sudo apt update && sudo apt install -y python3.7 python3.7-venv python3.9 python3.9-venv

# Install pip and tox for Python 3.7
python3.7 -m ensurepip && python3.7 -m pip --disable-pip-version-check --no-cache-dir install tox
