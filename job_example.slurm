#!/bin/bash
#SBATCH --job-name=dyme_process_node
#SBATCH --output=logs/dyme_%j.out
#SBATCH --error=logs/dyme_%j.err
#SBATCH --nodes=1                                #Number of nodes to run the node in
#SBATCH --ntasks=1                               #Leave at 1
#SBATCH --cpus-per-task=1                        #As many as desired. min 2 CPU per GPU card, min 16 and up to 256 for CPU node.
#SBATCH --gres=gpu:1                             #1 to 10, depending on how many GPUs per node you need. Delete line for CPU only node (scavenger)
#SBATCH --mem=2G                                 #2 GB per each 16 CPUs recommended
#SBATCH --time=160:00:00                          #Maximum time the node should stay up
#SBATCH --partition=your_partition_name_here     #partition name

#Add additional SLURM options here

# Load any required modules (cluster-specific)
module load apptainer                   # aptainer is required to run the node

# Set variables
MAIN_NODE=hostname_or_ip                # This is the hostname or IP of the server running the Main Node
NODE_TYPE=MD                            # This should be MD or scavenger
CONTAINER_IMAGE=/path/to/directory      # This should point to a network drive where your nodes can read "dyme_node.sif" and "launch_node.sh"
PROJECT_DATA_DIR=/path/to/dyme_projects # This is the shared network drive where your DyME files are located. As provided during install.

# This command runs the DyME Node container
.${CONTAINER_IMAGE}/launch_node.sh ${NODE_TYPE} ${MAIN_NODE} ${PROJECT_DATA_DIR} &
wait 
