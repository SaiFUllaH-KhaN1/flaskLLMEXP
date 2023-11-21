#!/bin/bash

# Install portaudio19-dev
sudo apt-get update
sudo apt-get install -y portaudio19-dev

# Install Python dependencies
pip install -r requirements.txt
