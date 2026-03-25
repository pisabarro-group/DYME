# DYME (Dynamic Mutagenesis Engine)

## Overview

DYME is a computational platform for automated large-scale molecular dynamics (MD) analysis and high-throughput mutational exploration. It orchestrates MD simulations and visual comparative analysis into a single workflow.

The system is made of two main components:
- **dyme_main**: A central server (Docker) serving a central database, web UI and RESTful API
- **dyme_node**: A worker container (Singularity/Apptainer) executing MD and scavenging tasks

---

## Architecture

- **Main Node (Docker)**
  - Runs MongoDB and other backend services
  - Exposes ports:
    - `8080` (API/UI)
    - `27017` (MongoDB access)

- **Worker Nodes (Apptainer/Singularity)**
  - Runs in as many distributed servers as desired. Executes tasks in two modes:
    - `MD` → runs simulations (GPU-only)
    - `scavenger` → processes completed MD trajectories (CPU-only)

- **Shared Storage**
  - All nodes must access a common filesystem 
  - Recommended: Network-mounted directory (NFS)

DyME runs in Linux (x86_64) hardware. We highly recommend a debian-based distro (Ubuntu ≥ 22.04) or RHEL based distros. Other distros are not currently supported by the installer.

---

## Build and Install Requirements

The DyME installer and its execution depend on third-party components:

- Docker (for main node)
- BuildX (Docker build plugin)
- Apptainer / Singularity ≥ 3.10 (for worker node deployment)

- A Salilab's MODELLER license
  (Request your free academic license here: https://salilab.org/modeller/registration.html)
 

---

## Minimum Hardware Recommendations

- **Main Node**
  - 4 CPUs
  - 8–32 GB RAM

- **Worker Nodes**
  - At least 8 CPUs for scavenger nodes (64 to 256 CPUs recommended)
  - At least 1 GPU card for MD nodes (CUDA-compatible)
  
- **Storage**
  - 20GB for installing + building the system (at the main node server)
  - Enough space for hundreds of MD simulations (several GB to several TB)
  - User must have have write-permissions in the shared partition
    
- **Network**
  - All nodes (main and worker) should reside in the same network (recommended)
  - Distributed networks will work as long as the worker nodes can ping the main node.
      
---

## Installation

The DyME installer automatically builds the platform for you. To begin, login to the console of the machine that will act as "Main Node" and navigate to a suitable directory. Make sure you have at least 20Gb available.

1) Clone the DYME repository, and execute the installer:

```bash
git clone https://github.com/pisabarro-group/DYME.git
cd DYME
chmod a+x install.sh
./install.sh
```

The installer will check for pre-requisites and attempt to install missing dependencies (Docker, BuildX Apptainer, curl, and others). It will also verify if your user has permissions to run docker containers. If the installer is unable to solve the dependencies, install them manually - and run the installer again.

The installer will create the necesary directory structures in the provided directory PATH. This path will bind to the internal directory `/dyme_root` in all containers.

2) The installer will build:
- A Docker image called `dyme_main` (This is your main server)
- A Singularity `.sif` image for container `dyme_node` (This contains worker nodes)


3) Upon completion DyME should be running on your Docker server. You can access the UI by entering http://server_hostname:8080 in your browser.


---

## Test Data

If you would like to install test-data, answer "y" when prompted to do so by the installer. The DyME test-data  will be downloaded from here (https://zenodo.org/records/18014320). It contains approx. ~11GB of MD simulations.


**IT IS NOT NECESARY TO MANUALLY DOWNLOAD THE TEST DATA - THE INSTALLER WILL DO IT FOR YOU**

---

## Running The Main Node

The following commands can be used to control the container (start or stop):

### Main node start

Replace "/path/to/filesystem" with the folder you provided during installation.

```bash
   docker run \
        --name dyme_main \
        -d \
        -v "/path/to/filesystem:/dyme_root" \
        -p 8080:80 \
        -p 27017:27017 \
        dyme_main:latest
```

To stop a running DyME Main node, execute the following cmd:
### Main node stop
```bash
   docker stop dyme_main
```

---

## Running Workers

Worker nodes reside in the .sif container called `dyme_node.sif`. It should have been created in the same directory where DyME was cloned. This file is **portable**. It can be copied to remote servers, HPC partitions or shared locations.

- You need Apptainer (or Singularity) installed to launch a worker node.
- The container can run manually from the console, or masively using queue managers (i.e. SLURM).


### Tip:
DyME includes a wrapper script (launch_node.sh) to facilitate launching worker nodes on any machine. 
Keep in mind this script requires the .sif container to be located in the same directory.

The syntax to use the wrapper is:
```bash
./launch_node.sh <nodetype> <dbhostname> </path/to/shared/data>
```

### Parameters

- `nodetype`:
  - `MD` → simulation node (uses GPU via `--nv`)
  - `scavenger` → analysis node (CPU only)

- `dbhostname`:
  - hostname or IP of the main node

- `path`:
  - shared directory mounted across all nodes


If you would like to start the worker manually. using Apptainer, modify the required variables manually and execute the following command:

```bash
 export BINDPATH=/path/to/shared/directory
 export SIF_IMAGE=dyme_node.sif
 export NODETYPE=MD
 export DBHOST=name_of_main_dyme_server

 apptainer --nv exec \
    --bind "$BINDPATH":"/dyme_root" \
    --bind /dev/shm:/dev/shm \
    "$SIF_IMAGE" \
    "$NODETYPE" "$DBHOST"
```

---

### Examples

```bash
./launchworker.sh MD 192.168.1.10 /group/dyme_data
```

```bash
./launchworker.sh scavenger localhost /data/dyme
```

---

## Execution Behavior

### MD Node
- Runs MD simulation workloads
- Continuously polls database
- Uses GPU acceleration (`--nv`)
- Deploys ONE simulation per idle GPU card
- Safe for multi-node execution (atomic DB claiming)

### Scavenger Node (default behavior)
- Continuously polls database
- Selects mutants with:
  status = "ready_to_scavenge"
- Processes mutants in batches:
  batch_size = available_cpus // 8
- Works across all projects automatically
- Safe for multi-node execution (atomic DB claiming)

---

## Notes

- Multiple scavenger nodes can run concurrently
- No external scheduler required for scavenging
- Database ensures no duplicate processing

---