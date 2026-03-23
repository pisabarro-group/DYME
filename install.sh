#!/bin/bash
#"""
#DYME - Dynamic Mutagenesis Engine v1.0
#File:  install.sh

#Author:     
#Pedro Manuel Guillem Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>
#Structural Bioinformatics Laboratory 
#BIOTEC - Pisabarro Group
#Technische Universität Dresden, 2026

#Licensing:
# 
# Copyright (c) 2026 Pedro Guillem, Gloria Ruiz-Gomez, MT-Pisabarro

# This software is licensed for **academic, educational, and non-commercial research use only**.
# You may use, modify, and distribute the source code for academic purposes provided you:
# 
#   • Retain this copyright notice
#   • Cite the author(s) in publications using this software
#   • Comply with any third-party licenses
# 
# **Commercial use** (including in proprietary software, SaaS platforms, or consulting services)
# requires a separate commercial license agreement from the author.

# ⚠️ Note: This distribution includes third-party components under MIT, BSD, and GPL licenses.
# When using these components, you must comply with their respective licenses as described in
# `LICENSES.txt`.

#   !!!!!!!!!!!!!!
#   IMPORTANT!
#   !!!!!!!!!!!!!!
#    
#   DyME is meant to run in local networks (where internet security is not a concern).
#   THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND. 
##
###


# Step 1: Display License Agreement
clear
echo " ____      _____ _____ "
echo "|    \ _ _|     |   __|"
echo "|  |  | | | | | |   __|"
echo "|____/|_  |_|_|_|_____| (Dynamic Mutagenesis Engine v1.0)"
echo "      |___|             (Pedro M. Guillem-Gloria | Structural Bioinformatics | TU Dresden 2026)"
echo "------------------------------------------------------------------------------------------"
echo "By using DyME and typing YES at this step, you agree with its Terms and Conditions."
echo "You should have received a copy of these terms (and LICENSE) along with this software."
echo ""

echo ""
echo "Type 'YES' to continue:"
read ACCEPT_LICENSE

if [ "$ACCEPT_LICENSE" != "YES" ]; then
    echo ""
    echo "License not accepted. Exiting."
    exit 1
fi

# Step 2: Clear the screen
clear


# Step 3: Request a valid local partition path
export DYME_PATH_DEFAULT=/opt/dyme
while true; do
echo " ____      _____ _____ "
echo "|    \ _ _|     |   __|"
echo "|  |  | | | | | |   __|"
echo "|____/|_  |_|_|_|_____| (Dynamic Mutagenesis Engine v1.0)"
echo "      |___|             (Pedro M. Guillem-Gloria | Structural Bioinformatics | TU Dresden 2026)"
echo "------------------------------------------------------------------------------------------"
echo ""
    echo "Provide a directory path for storing simulations, databases, logs and DyME assets"
    echo ""
    echo "- If running standalone, this path can be a local directory with read/write access"
    echo "- If running in a distributed environment, use a NFS share or drive acesible by all servers"
    echo ""
    read -p "Please enter the directory path (i.e. /opt/dyme/): " DYME_PATH

    if [ "$DYME_PATH" == "" ]; then
        export DYME_PATH=$DYME_PATH_DEFAULT
    fi

    if [ -d "$DYME_PATH" ]; then
        mkdir -p $DYME_PATH;
        mkdir -p $DYME_PATH/projects;
        mkdir -p $DYME_PATH/logs;
        mkdir -p $DYME_PATH/database/mongodb;
        mkdir -p $DYME_PATH/database/configdb;
        break
    else
        echo ""
        echo "The directory '$DYME_PATH' does not exist and will be created"
        echo ""
        echo "[press Enter to continue]" 
        read BLANK1
        mkdir -p $DYME_PATH;
        mkdir -p $DYME_PATH/projects;
        mkdir -p $DYME_PATH/logs;
        mkdir -p $DYME_PATH/database/mongodb
        mkdir -p $DYME_PATH/database/configdb
        if [ $? -eq 0 ]; then
                break
            else
                echo ""
                echo "Error: Could not create directories. Please check your user permissions and start over"
                echo ""
                exit 1
            fi
    fi
done


# Step 4: Clear the screen
clear

# Step 5: Request the MODELLER license key
while true; do
clear
echo " ____      _____ _____ "
echo "|    \ _ _|     |   __|"
echo "|  |  | | | | | |   __|"
echo "|____/|_  |_|_|_|_____| (Dynamic Mutagenesis Engine v1.0)"
echo "      |___|             (Pedro M. Guillem-Gloria | Structural Bioinformatics | TU Dresden 2026)"
echo "------------------------------------------------------------------------------------------"
echo ""
echo "DyME uses MODELLER (Salilab), which requires a license (free for academic use)"
echo "You can request one here: https://salilab.org/modeller/registration.html"
echo ""
    read -p "Please enter the MODELLER license key provided to you: " MODELLER_LICENSE
    if [ -n "$MODELLER_LICENSE" ]; then
        break
    else
        clear
        echo "Error: The MODELLER License key cannot be empty"
        echo "Please issue a license and run the installer again" 
        read BLANK1
        exit 1
    fi
done


# Step 6: Get hostname
clear
export dhs=$(hostname)
export HOST_IP=$(hostname -I | awk '{print $1}')
echo " ____      _____ _____ "
echo "|    \ _ _|     |   __|"
echo "|  |  | | | | | |   __|"
echo "|____/|_  |_|_|_|_____| (Dynamic Mutagenesis Engine v1.0)"
echo "      |___|             (Pedro M. Guillem-Gloria | Structural Bioinformatics | TU Dresden 2026)"
echo "------------------------------------------------------------------------------------------"
echo ""
echo "This server will be hosting the main node of DyME. Your hostnsme is: '$dhs'" 
echo ""
echo "If this is a valid hostname and is reachable from all servers in your network, simply click Enter"
read -p "Else, provide the IP address of this host (i.e. $HOST_IP): " DYME_HOST
if [ "$DYME_IP" != "" ]; then
    export dhs=$DYME_HOST
fi



clear
# Step 6: Run Docker build with collected inputs
echo " ____      _____ _____ "
echo "|    \ _ _|     |   __|"
echo "|  |  | | | | | |   __|"
echo "|____/|_  |_|_|_|_____| (Dynamic Mutagenesis Engine v1.0)"
echo "      |___|             (Pedro M. Guillem-Gloria | Structural Bioinformatics | TU Dresden 2026)"
echo "------------------------------------------------------------------------------------------"
echo ""
echo "Please verify that the following information is correct (or exit with Ctrl-C and start over):"
echo ""
echo "DyME Projects PATH: '$DYME_PATH'" 
echo "MODELLER license : '$MODELLER_LICENSE'"
echo "DyME Hostname (main node) : '$dhs'"
echo ""
read -p "[press Enter to continue]" BLANK1

# Step 4: Clear the screen
clear

#Get the current user's UID/GID
HOST_UID="$(id -u)"
HOST_GID="$(id -g)"

#Build Main Node
echo "Building dyme_main with UID=${HOST_UID} GID=${HOST_GID}"
echo "Building DyME Main-Node container. Get a coffee... this will take a while"
docker buildx build -f nodes/main_node/Dockerfile --build-arg DYME_UID="$HOST_UID" --build-arg DYME_GID="$HOST_GID" --output=type=docker --tag dyme_main --load .
docker save -o dyme_main.tar dyme_main
#docker run -it --rm -v /opt/dyme/projects:/dyme_root/projects   -v /opt/dyme/logs:/dyme_root/logs --entrypoint /bin/bash dyme_main


#Build MD/Scavenger node
echo "Building Worker Nodes container."
docker buildx build -f nodes/md_node/Dockerfile --output=type=docker --build-arg DYME_PATH="$DYME_PATH" --build-arg MODELLER_LICENSE="$MODELLER_LICENSE" --tag dyme_node --load .
docker save -o dyme_node.tar dyme_node

#Test 1 interactive bash
#docker run --rm --runtime=nvidia --gpus all -v $DYME_PATH:/dyme_root --tmpfs /mnt/ramdrive dyme_node MD pcpu1

echo ""
echo "Cleaning clutter..."
docker builder prune -f --verbose
echo ""

#Boot the main node, with the database
docker rm -f dyme_main 2>/dev/null || true
echo "Starting Main Node (container name: dyme_main)!"
echo "Running with DyME projects path at '$DYME_PATH'"
#docker run -d --name dyme_main -v $DYME_PATH:/dyme_root -p 8080:8080 -p 27017:27017 dyme_main:latest 

mkdir -p $DYME_PATH/logs $DYME_PATH/data/db $DYME_PATH/projects $DYME_PATH/nodes/source $DYME_PATH/database/mongodb
docker run --name dyme_main -d -v $DYME_PATH:/dyme_root -p 8080:80 -p 27017:27017 dyme_main:latest 


echo "Waiting for MongoDB to start..."
until docker exec dyme_main mongo --eval "db.adminCommand('ping')" &>/dev/null; do
  sleep 2
done
echo "Cool...MongoDB is up and running in the Dyme main node!"
sleep 1
echo ""
echo "Populating initial database structures"


docker exec dyme_main mongo dyme --eval "db.default_settings.insertOne({  \
    \"www_path\": \"/dyme_base\", \
    \"hdd_path\": \"$DYME_PATH\", \
    \"hpc_path\": \"$DYME_PATH\", \
    \"hpc_path2\": \"$DYME_PATH\", \
    \"tmpfile_dir\": \"/tmp\", \
    \"project_dir\": \"/projects\", \
    \"frontend_dir\": \"/frontend\", \
    \"backend_dir\": \"/backend\", \
    \"hostname\": \"$dhs\" \
})"

docker cp ./nodes/main_node/dyme_backup dyme_main:/dyme_backup
docker exec -it dyme_main mongorestore --db dyme --dir /dyme_backup/dyme
echo "Loaded base collection metadata into DB"
echo "---------------------------------------------------"
echo "---------------------------------------------------"
echo ""


download_tar() {

    TAR_FILE="dyme-test-data-md.tar"
    ZENODO_URL="https://zenodo.org/records/18014320/files/dyme-test-data-md.tar?download=1"

    echo "Downloading test data (11 GB)..."
    curl -L --fail --output "$TAR_FILE" "$ZENODO_URL"
    echo "Download completed: $TAR_FILE"

    #Unpack MD trajectories in project folder
    echo "Unpacking MD trajectories to projects folder"
    tar -xf dyme-test-data-md.tar -C "$DYME_PATH/projects"

    #Import test data database records (Approx 22Mb)
    echo "Loading test data records into Database"
    docker exec -it dyme_main mongoimport --db dyme --collection projects --file /dyme_backup/projects.json --jsonArray
    docker exec -it dyme_main mongoimport --db dyme --collection mutants --file /dyme_backup/mutants.json --jsonArray
    docker exec -it dyme_main mongoimport --db dyme --collection processed_data --file /dyme_backup/processed_data.json --jsonArray

    #UPDATE PROJECT FOLDERS IN INTERNAL DB TO MATCH DYME_PATH
    docker exec dyme_main mongosh dyme --eval \
    'db.projects.updateOne({id_project: 49}, {$set: {project_folder: "'"$DYME_PATH"'/projects/49"}})'

    docker exec dyme_main mongosh dyme --eval \
    'db.projects.updateOne({id_project: 50}, {$set: {project_folder: "'"$DYME_PATH"'/projects/50"}})'

    echo "Test Data - Load Complete :)"
    echo "---------------------------------------------------"
}

ask_download() {
    local answer
    read -r -p "Would you like to download and install MD test-data (11 GB) files from Zenodo? [y/N] " answer
    case "$answer" in
        [Yy]|[Yy][Ee][Ss]) download_tar ;;
        *)
            echo "Aborted."
            exit 0
            ;;
    esac
}

ask_download

echo "------------------------------------------------------------"
echo "       Install complete!!. Happy HTP mutagenesis :)"
echo "------------------------------------------------------------"
echo "Please cite our work if you found DyME useful"
echo ""
echo "[Pedro M. Guillem-Gloria, Gloria Ruiz-Gomez, MT-Pisabarro. The DYME Team]"
echo ""
echo "You can now access the DyME GUI from your browser: at http://$dhs"
echo "------------------------------------------------------------"
nohup xdg-open http://$dhs:8080&
