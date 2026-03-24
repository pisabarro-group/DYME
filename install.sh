#!/usr/bin/env bash

# DYME - Dynamic Mutagenesis Engine v1.0
# File: install.sh
#
# Author:
# Pedro Manuel Guillem Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>
# Structural Bioinformatics Laboratory
# BIOTEC - Pisabarro Group
# Technische Universität Dresden, 2026
#
# Licensing:
#
# Copyright (c) 2026 Pedro Guillem, Gloria Ruiz-Gomez, MT-Pisabarro
#
# This software is licensed for academic, educational, and non-commercial research use only under 
# the GPLv3 License. You may use, modify, and distribute the source code for academic purposes 
# provided you:
#   - Retain this copyright notice
#   - Cite the author(s) in publications using this software
#   - Comply with any third-party licenses (see publication for a full list of libraries)
#
# Commercial use (including in proprietary software, SaaS platforms, or consulting services)
# requires a separate commercial license agreement from the author.
#
# Note:
# This distribution includes third-party components under MIT, BSD, and GPL licenses.
# When using these components, you must comply with their respective licenses as described in
# LICENSES.txt.
#
# !!!!IMPORTANT!!!:
# DyME is meant to run in local networks where internet security is not a concern.
# This tool exposes a ports for web access, a database port without security and an API.
# Be aware none of these components have been hardened for IT security standards.
#
# BY USING DYME YOU ACCEPT THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
# AND YOU USE IT UNDER YOUR OWN RISK.

set -o errexit
set -o nounset
set -o pipefail

#######################################
# Globals
#######################################
DYME_PATH_DEFAULT="/opt/dyme"
SUPPORTED_OS_FAMILY=""
OS_ID=""
OS_VERSION_ID=""
PKG_MANAGER=""
SUDO=""
NEED_DOCKER_INSTALL=0
NEED_APPTAINER_INSTALL=0

#######################################
# UI helpers
#######################################
print_banner() {
    clear || true
    echo " ____      _____ _____ "
    echo "|    \\ _ _|     |   __|"
    echo "|  |  | | | | | |   __|"
    echo "|____/|_  |_|_|_|_____| (Dynamic Mutagenesis Engine v1.0)"
    echo "      |___|             (Pedro M. Guillem-Gloria | Structural Bioinformatics | TU Dresden 2026)"
    echo "------------------------------------------------------------------------------------------"
    echo ""
}

info() {
    echo "[INFO] $*"
}

warn() {
    echo "[WARN] $*" >&2
}

error() {
    echo "[ERROR] $*" >&2
}

die() {
    error "$*"
    exit 1
}

press_enter() {
    read -r -p "[press Enter to continue] " _
}

#######################################
# Command helpers
#######################################
have_cmd() {
    command -v "$1" >/dev/null 2>&1
}

run_quiet() {
    "$@" >/dev/null 2>&1
}

require_sudo_if_needed() {
    if [ "$(id -u)" -eq 0 ]; then
        SUDO=""
        return
    fi

    if have_cmd sudo; then
        if sudo -n true >/dev/null 2>&1; then
            SUDO="sudo"
        else
            info "Administrative privileges are required to install missing packages."
            info "You may be prompted for your password."
            sudo -v || die "sudo authentication failed."
            SUDO="sudo"
        fi
    else
        die "Missing 'sudo'. Re-run as root or install sudo."
    fi
}

#######################################
# OS detection
#######################################
detect_os() {
    [ -f /etc/os-release ] || die "/etc/os-release not found. Unsupported OS."

    # shellcheck disable=SC1091
    . /etc/os-release

    OS_ID="${ID:-unknown}"
    OS_VERSION_ID="${VERSION_ID:-unknown}"

    case "$OS_ID" in
        ubuntu|debian)
            SUPPORTED_OS_FAMILY="debian"
            PKG_MANAGER="apt"
            ;;
        rhel|centos|centos_stream|rocky|almalinux)
            SUPPORTED_OS_FAMILY="rhel"
            if have_cmd dnf; then
                PKG_MANAGER="dnf"
            elif have_cmd yum; then
                PKG_MANAGER="yum"
            else
                die "RHEL-like system detected, but neither dnf nor yum was found."
            fi
            ;;
        *)
            SUPPORTED_OS_FAMILY="unsupported"
            ;;
    esac
}

validate_supported_os() {
    case "$SUPPORTED_OS_FAMILY" in
        debian)
            case "$OS_ID" in
                ubuntu)
                    if ! awk "BEGIN {exit !($OS_VERSION_ID >= 22.04)}"; then
                        die "Unsupported Ubuntu version: $OS_VERSION_ID. Use Ubuntu 22.04 or later."
                    fi
                    ;;
                debian)
                    warn "Debian detected. Automatic package installation will be attempted, but DYME is officially supported on Ubuntu 22.04+."
                    ;;
            esac
            ;;
        rhel)
            warn "RHEL/CentOS-like system detected: $OS_ID $OS_VERSION_ID"
            warn "Automatic installation will be attempted where possible."
            ;;
        *)
            die "Unsupported OS: $OS_ID $OS_VERSION_ID. Please install curl, docker, docker buildx, and apptainer manually."
            ;;
    esac
}

#######################################
# Package installation
#######################################
apt_update_once() {
    if [ ! -f /tmp/.dyme_apt_updated ]; then
        $SUDO apt-get update -y
        touch /tmp/.dyme_apt_updated
    fi
}

install_packages_apt() {
    apt_update_once
    $SUDO apt-get install -y "$@"
}

install_packages_rhel() {
    "$SUDO" "$PKG_MANAGER" install -y "$@"
}

install_docker_debian() {
    info "Attempting to install Docker and buildx on Debian/Ubuntu..."

    if install_packages_apt ca-certificates curl gnupg lsb-release docker.io docker-buildx-plugin; then
        return 0
    fi

    warn "Distro package install failed. Trying fallback packages..."
    install_packages_apt ca-certificates curl gnupg lsb-release docker.io || return 1

    return 0
}

install_apptainer_debian() {
    info "Attempting to install Apptainer on Debian/Ubuntu..."

    apt_update_once

    if install_packages_apt apptainer; then
        return 0
    fi

    warn "Package 'apptainer' not found in standard repositories."
    warn "On some Debian-based systems, Apptainer is not available from default repos."
    return 1
}

install_docker_rhel() {
    info "Attempting to install Docker and buildx on RHEL/CentOS-like system..."

    if "$SUDO" "$PKG_MANAGER" install -y docker docker-buildx-plugin; then
        return 0
    fi

    warn "Could not install docker/docker-buildx-plugin from default repositories."
    return 1
}

install_apptainer_rhel() {
    info "Attempting to install Apptainer on RHEL/CentOS-like system..."

    if "$SUDO" "$PKG_MANAGER" install -y apptainer; then
        return 0
    fi

    warn "Could not install Apptainer from default repositories."
    return 1
}

ensure_docker_service_running() {
    if ! have_cmd docker; then
        return 1
    fi

    if run_quiet docker info; then
        return 0
    fi

    warn "Docker is installed but not currently usable by the current user."

    if [ -n "$SUDO" ]; then
        info "Attempting to enable and start the Docker service..."
        $SUDO systemctl enable docker >/dev/null 2>&1 || true
        $SUDO systemctl start docker >/dev/null 2>&1 || true
    fi

    if run_quiet docker info; then
        return 0
    fi

    if [ -n "$SUDO" ]; then
        warn "Attempting to add user '$USER' to the docker group..."
        $SUDO groupadd -f docker >/dev/null 2>&1 || true
        $SUDO usermod -aG docker "$USER" || true
    fi

    info "Re-checking Docker access in the current session..."
    if run_quiet docker info; then
        return 0
    fi

    echo ""
    warn "Docker still cannot be executed by the current user in this session."
    warn "Please log out and log in again, then rerun this installer."
    warn "If Docker still does not work after that, please check your system configuration manually."
    return 1
}

ensure_requirements() {
    print_banner
    info "Checking operating system..."
    detect_os
    validate_supported_os

    info "Detected OS: $OS_ID $OS_VERSION_ID"
    info "Package manager: $PKG_MANAGER"
    echo ""

    if ! have_cmd curl; then
        warn "Missing required command: curl"
        require_sudo_if_needed

        case "$SUPPORTED_OS_FAMILY" in
            debian)
                install_packages_apt curl || die "Could not install curl automatically. Please install it manually and rerun."
                ;;
            rhel)
                install_packages_rhel curl || die "Could not install curl automatically. Please install it manually and rerun."
                ;;
        esac
    fi

    if ! have_cmd docker; then
        NEED_DOCKER_INSTALL=1
        warn "Missing required command: docker"
    fi

    if have_cmd docker; then
        if ! docker buildx version >/dev/null 2>&1; then
            NEED_DOCKER_INSTALL=1
            warn "Docker found, but 'docker buildx' is not available."
        fi
    fi

    if ! have_cmd apptainer; then
        NEED_APPTAINER_INSTALL=1
        warn "Missing required command: apptainer"
    fi

    if [ "$NEED_DOCKER_INSTALL" -eq 1 ] || [ "$NEED_APPTAINER_INSTALL" -eq 1 ]; then
        require_sudo_if_needed
    fi

    if [ "$NEED_DOCKER_INSTALL" -eq 1 ]; then
        case "$SUPPORTED_OS_FAMILY" in
            debian)
                install_docker_debian || die "Could not install Docker/buildx automatically. Please install them manually and rerun."
                ;;
            rhel)
                install_docker_rhel || die "Could not install Docker/buildx automatically. Please install them manually and rerun."
                ;;
        esac
    fi

    if [ "$NEED_APPTAINER_INSTALL" -eq 1 ]; then
        case "$SUPPORTED_OS_FAMILY" in
            debian)
                install_apptainer_debian || die "Could not install Apptainer automatically. Please install it manually and rerun."
                ;;
            rhel)
                install_apptainer_rhel || die "Could not install Apptainer automatically. Please install it manually and rerun."
                ;;
        esac
    fi

    have_cmd curl || die "'curl' is still missing after installation attempt."
    have_cmd docker || die "'docker' is still missing after installation attempt."
    docker buildx version >/dev/null 2>&1 || die "'docker buildx' is still unavailable after installation attempt."
    have_cmd apptainer || die "'apptainer' is still missing after installation attempt."

    ensure_docker_service_running || die "Docker is installed but the current user cannot execute it."
    apptainer --version >/dev/null 2>&1 || die "Apptainer is installed but cannot be executed by the current user."

    info "All required tools are present and executable."
    press_enter
}

#######################################
# License / input steps
#######################################
accept_license() {
    print_banner
    echo "By using DyME and typing YES at this step, you agree with its Terms and Conditions."
    echo "You should have received a copy of these terms (and LICENSE) along with this software."
    echo ""
    read -r -p "Type 'YES' to continue: " ACCEPT_LICENSE

    if [ "$ACCEPT_LICENSE" != "YES" ]; then
        echo ""
        die "License not accepted. Exiting."
    fi
}

prompt_dyme_path() {
    while true; do
        print_banner
        echo "Provide a directory path for storing simulations, databases, logs and DyME assets"
        echo ""
        echo "- If running standalone, this path can be a local directory with read/write access"
        echo "- If running in a distributed environment, use a NFS share or drive accessible by all servers"
        echo ""

        read -r -p "Please enter the directory path (i.e. /opt/dyme/): " DYME_PATH

        if [ -z "$DYME_PATH" ]; then
            DYME_PATH="$DYME_PATH_DEFAULT"
        fi

        if mkdir -p "$DYME_PATH" \
                    "$DYME_PATH/projects" \
                    "$DYME_PATH/logs" \
                    "$DYME_PATH/database/mongodb" \
                    "$DYME_PATH/database/configdb"; then
            break
        else
            echo ""
            warn "Could not create '$DYME_PATH'. Please check your permissions."
            press_enter
        fi
    done
}

prompt_modeller_license() {
    while true; do
        print_banner
        echo "DyME uses MODELLER (Salilab), which requires a license (free for academic use)"
        echo "You can request one here: https://salilab.org/modeller/registration.html"
        echo ""

        read -r -p "Please enter the MODELLER license key provided to you: " MODELLER_LICENSE
        if [ -n "$MODELLER_LICENSE" ]; then
            break
        fi

        warn "The MODELLER license key cannot be empty."
        press_enter
    done
}

prompt_hostname() {
    print_banner

    dhs="$(hostname)"
    HOST_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"

    echo "This server will be hosting the main node of DyME."
    echo "Detected hostname: '$dhs'"
    echo ""

    if [ -n "${HOST_IP:-}" ]; then
        read -r -p "If hostname is not reachable, provide the IP address of this host (i.e. $HOST_IP): " DYME_HOST
    else
        read -r -p "If hostname is not reachable, provide the IP address of this host: " DYME_HOST
    fi

    if [ -n "${DYME_HOST:-}" ]; then
        dhs="$DYME_HOST"
    fi
}

confirm_inputs() {
    print_banner
    echo "Please verify that the following information is correct:"
    echo ""
    echo "DyME Projects PATH          : '$DYME_PATH'"
    echo "MODELLER license            : '$MODELLER_LICENSE'"
    echo "DyME Hostname / main node   : '$dhs'"
    echo ""
    press_enter
}

#######################################
# Build / run steps
#######################################
build_images() {
    HOST_UID="$(id -u)"
    HOST_GID="$(id -g)"

    print_banner
    info "Building dyme_main with UID=${HOST_UID} GID=${HOST_GID}"
    info "Building DyME Main-Node container. This may take a while."

    docker buildx build \
        -f nodes/main_node/Dockerfile \
        --build-arg DYME_UID="$HOST_UID" \
        --build-arg DYME_GID="$HOST_GID" \
        --build-arg MODELLER_LICENSE="$MODELLER_LICENSE" \
        --output=type=docker \
        --tag dyme_main \
        --load .

    info "DYME MAIN NODE BUILT"
    info "Exporting image to tar file..."
    docker save -o dyme_main.tar dyme_main

    info "Building Worker Nodes container..."
    docker buildx build \
        -f nodes/md_node/Dockerfile \
        --output=type=docker \
        --build-arg DYME_PATH="$DYME_PATH" \
        --build-arg MODELLER_LICENSE="$MODELLER_LICENSE" \
        --tag dyme_node \
        --load .

    info "DYME WORKER NODE BUILT"
    info "Exporting image to tar file..."
    docker save -o dyme_node.tar dyme_node

    # Build the apptainer (singularity) container for dyme_node
    # apptainer build dyme_node.sif docker-archive://dyme_node.tar
      apptainer build dyme_node.sif docker-daemon://dyme_node:latest
}

start_main_node() {
    print_banner
    info "Cleaning Docker builder cache..."
    docker builder prune -f >/dev/null 2>&1 || true

    info "Removing old dyme_main container if present..."
    docker rm -f dyme_main >/dev/null 2>&1 || true

    info "Starting Main Node (container name: dyme_main)"
    info "Using DyME projects path at '$DYME_PATH'"

    mkdir -p \
        "$DYME_PATH/logs" \
        "$DYME_PATH/data/db" \
        "$DYME_PATH/projects" \
        "$DYME_PATH/nodes/source" \
        "$DYME_PATH/database/mongodb"

    docker run \
        --name dyme_main \
        -d \
        -v "$DYME_PATH:/dyme_root" \
        -p 8080:80 \
        -p 27017:27017 \
        dyme_main:latest

    info "Waiting for MongoDB to start..."
    until docker exec dyme_main mongosh --eval "db.adminCommand({ ping: 1 })" >/dev/null 2>&1; do
        sleep 2
    done

    info "MongoDB is up."
    info "Populating initial database structures..."

    docker exec dyme_main mongosh dyme --eval 'db.default_settings.insertOne({
      www_path: "/dyme_base",
      hdd_path: "/dyme_root",
      hpc_path: "/dyme_root",
      hpc_path2: "/dyme_root",
      tmpfile_dir: "/tmp",
      project_dir: "/projects",
      frontend_dir: "/frontend",
      backend_dir: "/backend",
      hostname: "'"$dhs"'"
    })'

    docker cp ./nodes/main_node/dyme_backup dyme_main:/dyme_backup
    docker exec dyme_main mongorestore --db dyme --dir /dyme_backup/dyme

    info "Loaded base collection metadata into DB."
}

download_tar() {
    TAR_FILE="dyme-test-data-md.tar"
    ZENODO_URL="https://zenodo.org/records/18014320/files/dyme-test-data-md.tar?download=1"

    info "Downloading test data from Zenodo..."
    curl -L --fail --output "$TAR_FILE" "$ZENODO_URL"

    info "Unpacking MD trajectories into projects folder..."
    tar -xf "$TAR_FILE" -C "$DYME_PATH/projects"

    info "Loading test data records into database..."
    docker exec dyme_main mongoimport --db dyme --collection projects --file /dyme_backup/projects.json --jsonArray
    docker exec dyme_main mongoimport --db dyme --collection mutants --file /dyme_backup/mutants.json --jsonArray
    docker exec dyme_main mongoimport --db dyme --collection processed_data --file /dyme_backup/processed_data.json --jsonArray

    info "Updating project folders in internal DB..."
    docker exec dyme_main mongosh dyme --eval \
        'db.projects.updateOne({id_project: 49}, {$set: {project_folder: "/dyme_root/projects/49"}})'

    docker exec dyme_main mongosh dyme --eval \
        'db.projects.updateOne({id_project: 50}, {$set: {project_folder: "/dyme_root/projects/50"}})'

    info "Test data load complete."
}

ask_download() {
    local answer
    echo ""
    read -r -p "Would you like to download and install MD test-data (11 GB) files from Zenodo? [y/N] " answer
    case "$answer" in
        [Yy]|[Yy][Ee][Ss])
            download_tar
            ;;
        *)
            info "Skipping test data download."
            ;;
    esac
}

finish_message() {
    print_banner
    echo "------------------------------------------------------------"
    echo "       Install complete. Happy HTP mutagenesis :)"
    echo "------------------------------------------------------------"
    echo "Please cite our work if you found DyME useful"
    echo ""
    echo "[Pedro M. Guillem-Gloria, Gloria Ruiz-Gomez, MT-Pisabarro. The DYME Team]"
    echo ""
    echo "You can now access the DyME GUI from your browser at:"
    echo "http://$dhs:8080"
    echo "------------------------------------------------------------"

    if have_cmd xdg-open; then
        nohup xdg-open "http://$dhs:8080" >/dev/null 2>&1 || true
    fi
}

#######################################
# Main
#######################################
main() {
    ensure_requirements
    accept_license
    prompt_dyme_path
    prompt_modeller_license
    prompt_hostname
    confirm_inputs
    build_images
    start_main_node
    ask_download
    finish_message
}

main "$@"