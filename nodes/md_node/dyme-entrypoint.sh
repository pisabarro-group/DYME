#!/usr/bin/env bash
mkdir -p /dyme_root/logs /dyme_root/data/db /dyme_root/projects /dyme_root/nodes/source /dyme_root/database/mongodb

init_conda() {
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

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <nodetype [MD or scavenger]> <dbhost>"
  exit 1
fi

NODETYPE="$1"
DBHOST="$2"
PROJ="$3"
MUT="$4"

case "$NODETYPE" in
  scavenger)
    echo "Starting Scavenger.py with dbhost: $DBHOST"
    init_conda
    exec python /dyme_base/backend/dyme/Scavenger_slurm.py -d "$DBHOST" -p "$PROJ" -m "$MUT"
    ;;
  MD)
    echo "Starting MD.py with dbhost: $DBHOST"
    init_conda
    exec python /dyme_base/backend/dyme/MD.py -d "$DBHOST"
    ;;
  *)
    echo "Unknown nodetype: $NODETYPE. Expected 'scavenger' or 'MD'."
    exit 1
    ;;
esac



