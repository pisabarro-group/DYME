#!/usr/bin/env bash
# entrypoint.sh

# Activate the conda environment that was installed to /dyme_node
source /opt/miniconda/bin/activate /dyme_node

# Pass the single parameter ($1) directly to a Python script that depends on the conda env.
# Adjust this to point to whatever Python script you actually want to run.
python /dyme_node/Scavenger_node.py --scavengeall 1 --host "$1"
