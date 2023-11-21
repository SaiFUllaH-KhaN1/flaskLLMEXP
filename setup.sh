#!/bin/bash

# Install portaudio19-dev
apt-get update
apt-get install -y portaudio19-dev

# Install Python dependencies
pip install -r requirements.txt
