#!/usr/bin/env bash
mkdir -p /dyme_root/logs /dyme_root/data/db /dyme_root/projects /dyme_root/nodes/source /dyme_root/database/mongodb

init_conda() {
    echo "Initializing DYME environment, please wait"
    # >>> conda initialize >>>
    # !! Contents within this block are managed by 'conda init' !!
    __conda_setup="$('/dyme_env/anaconda/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
    if [ $? -eq 0 ]; then
        eval "$__conda_setup"
    else
        if [ -f "/dyme_env/anaconda/etc/profile.d/conda.sh" ]; then
            . "/dyme_env/anaconda/etc/profile.d/conda.sh"
        else
            export PATH="/dyme_env/anaconda/bin:$PATH"
        fi
    fi
    unset __conda_setup
    # <<< conda initialize <<<
    conda activate dyme_nodes
}

if [ "$#" -eq 0 ]; then
  echo "You must provide the node to launch (MD or scavenger) and the IP or hostname of the Main node"
  echo "- The node must be reachable from here"
  echo "- Don't forget to --bind the container /dyme_root to yout NFS share path"
  echo ""
  echo "Usage: $0 MD <dbhost> <reusegpus>"
  echo "Usage: $0 scavenger <dbhost>"
  exit 1
fi

NODETYPE="$1"
DBHOST="$2"
PROJ="$3"

case "$NODETYPE" in
  scavenger)
    echo "Starting Scavenger.py with dbhost: $DBHOST"
    init_conda
    exec python /dyme_base/backend/dyme/Scavenger_slurm.py "$DBHOST"
    ;;
  MD)
    echo "Starting MD.py with dbhost: $DBHOST"
    init_conda
    if [ -n "$PROJ" ]; then
      exec python /dyme_base/backend/dyme/MD.py -d "$DBHOST" -u
    else
      exec python /dyme_base/backend/dyme/MD.py -d "$DBHOST"
    fi
    
    ;;
  *)
    echo "Unknown nodetype: $NODETYPE. Expected 'scavenger' or 'MD'."
    exit 1
    ;;
esac



