#!/usr/bin/env bash

#This file is a simple wrapper for apptainer, so you don't have to write a long command
#usage: ./launch_node.sh <nodetype MD|scavenger> <dbhostname> <path_to_dymeroot>
#Example:
# 
# ./launch_node.sh MD dymeserver /path/to/your/shared/dyme/root


#Author:     
#Pedro Manuel Guillem Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>
#Structural Bioinformatics Laboratory - BIOTEC - Pisabarro Group
#Technische Universität Dresden



#!/usr/bin/env bash

set -e

# ==============================
# Usage
# ==============================
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <nodetype: MD|scavenger> <dbhostname> </path/to/dir>"
    exit 1
fi

NODETYPE="$1"
DBHOST="$2"
BINDPATH="$3"

# ==============================
# Validate nodetype
# ==============================
if [[ "$NODETYPE" != "MD" && "$NODETYPE" != "scavenger" ]]; then
    echo "Error: nodetype must be 'MD' or 'scavenger'"
    exit 1
fi

# ==============================
# Config
# ==============================
SIF_IMAGE="dyme_node.sif"
CONTAINER_WORKDIR="/dyme_root"

# ==============================
# Sanity checks
# ==============================
if [ ! -f "$SIF_IMAGE" ]; then
    echo "Error: SIF image '$SIF_IMAGE' not found"
    exit 1
fi

if [ ! -d "$BINDPATH" ]; then
    echo "Error: bind path '$BINDPATH' does not exist"
    exit 1
fi

# ==============================
# Launch
# ==============================
echo "Launching DYME worker"
echo "Type: $NODETYPE | DB: $DBHOST | Bind: $BINDPATH"

if [ "$NODETYPE" = "MD" ]; then
    apptainer run --nv \
        --bind "$BINDPATH":"$CONTAINER_WORKDIR" \
        "$SIF_IMAGE" \
        "$NODETYPE" "$DBHOST"
else
    apptainer run \
        --bind "$BINDPATH":"$CONTAINER_WORKDIR" \
        "$SIF_IMAGE" \
        "$NODETYPE" "$DBHOST"
fi