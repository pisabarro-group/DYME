# -*- coding: utf-8 -*-
"""
DYME - Dynamic Mutagenesis Engine v0.1

File:           Scavenger_slurm.py
Description:    Mutagenesis Generator Class

Purpose:        -Provides functions to scavenge data from trajectories
                 This version of the scavenger deploys pending jobs without using the SLURM workload manager 
                 You can deploy as many instances as you need WITH your own slurm file.

Provides:       -class Scavenger()

Author:     
Pedro Manuel Guillem Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>
Structural Bioinformatics Laboratory - BIOTEC - Pisabarro Group
Technische Universität Dresden

Mar 2023 - Built the whole thing... >)
May 2023 - We have issues with failing file handles when the process queue is too long. 
Nov 2023 - Built this version of the Scavenger... runs once.. assigns 8 CPUs per mutant automatically

"""

#import mdanalysis as mda
import mdtraj as md
import parmed as parm

import sys
import os
from multiprocessing import Pool
from pymongo import ReturnDocument
import subprocess
import time
from socket import gethostname
import argparse

# OWN
import Node
from DymeTools import InputSystem, MMGBSA, WaterMapper, Contacts
from DymeDB import DymeDB

#Count the available CPUs in the system.. we also try to get if we are in slurm and use ntasks and CPUs per task
def get_available_cpus():
    slurm_cpt = os.environ.get("SLURM_CPUS_PER_TASK")
    slurm_ntasks = os.environ.get("SLURM_NTASKS")

    affinity_cpus = None
    if hasattr(os, "sched_getaffinity"):
        try:
            affinity_cpus = len(os.sched_getaffinity(0))
        except Exception:
            affinity_cpus = None

    if slurm_cpt and slurm_ntasks:
        return int(slurm_cpt) * int(slurm_ntasks)

    if slurm_cpt:
        return int(slurm_cpt)

    return affinity_cpus or (os.cpu_count() or 1)

#Get everything about a mutant, and the paths required for all DyMEtools to process properly
def get_mutant_dirs(default_settings, mutID, projID):
    dirs = {}
    base_path = default_settings["hdd_path"] + default_settings["project_dir"] + "/" + str(projID)

    dirs["mutant"]  = f'{base_path}/mutants/{mutID}/'
    dirs["inputs"]  = f'{base_path}/mutants/{mutID}/inputs/'
    dirs["outputs"] = f'{base_path}/mutants/{mutID}/outputs/'
    dirs["ramdisk_in"]  = f'/mnt/ramdisk/{projID}/mutants/{mutID}/inputs/'
    dirs["ramdisk_out"] = f'/mnt/ramdisk/{projID}/mutants/{mutID}/outputs/'

    os.makedirs(dirs["ramdisk_in"], exist_ok=True)
    os.makedirs(dirs["ramdisk_out"], exist_ok=True)

    return dirs

#This is the main process that gets executed in the pool. One per mutant. 
#It also calls its own DymeDB handler.
def compute_energies_worker(args):
    import gc
    import shutil
    from datetime import datetime

    mutantID, projectID, dbhost, hostname, cpus_per_energyprocess, output_md = args
    #Connect to DyME
    db = DymeDB(dbhost)
    default_settings = db.select_document("default_settings", {})
    project = db.select_document("projects", {"id_project": projectID})
    paths   = get_mutant_dirs(default_settings, mutantID, projectID)

    q = {'id_project': int(projectID), 'mutantID': int(mutantID)}
    timestart = int(time.time())
    workdir = None

    try:
        igbVal = project["inputs"].get("igb", 2)
        inpVal = project["inputs"].get("inp", 1)
        energ = "energy_pbsa" if "energy_pbsa" in project["analysis"] else "energy_gbsa"

        pid = MMGBSA(
            mutantID=int(mutantID),
            outPath=paths["mutant"],
            interval=30,
            igb=igbVal,
            inp=inpVal,
            compute_mode=energ
        )

        pid.setRamDisk(paths["ramdisk_in"], paths["ramdisk_out"])
        pid.makeInputs()
        pid.writeInputs()
        codes = pid.launchCodes(cpus_per_energyprocess)

        db.dbtable_mutants.update_one(q, {"$set": {
            'status': 'scavenging_GBSA_pairwise',
            "status_vars.scavenger_node": hostname,
            "status_vars.scavenger_start_time": datetime.now(),
            "status_vars.scavenger_start_time_seconds": timestart,
            "status_vars.scavenger_progress_percentage": 0
        }})

        pid.genNCtrajectory(paths["mutant"])

        cmd = codes["pairwise"]
        p = subprocess.Popen([f'{cmd}'], cwd=paths["ramdisk_in"], shell=True, executable='/bin/bash')
        p.communicate()

        db.dbtable_mutants.update_one(q, {"$set": {
            'status': 'scavenging_GBSA_perresidue',
            "status_vars.scavenger_progress_percentage": 40
        }})

        cmd = codes["perresidue"]
        p = subprocess.Popen([f'{cmd}'], cwd=paths["ramdisk_in"], shell=True, executable='/bin/bash')
        p.communicate()

        anchorpoints = []
        for cluster in project["clusters"]:
            if cluster:
                anchorpoints += cluster

        db.dbtable_mutants.update_one(q, {"$set": {
            'status': 'scavenging_deltas_table',
            "status_vars.scavenger_progress_percentage": 80
        }})

        delta_g    = pid.parse_deltaG() #Get total binding energy
        perresidue = pid.parse_Perresidue() #get perresidue
        pairwise   = pid.parse_Pairwise(anchorpoints) #get pairwise
        bestframe  = pid.parse_BestFrame() #Same for best frame of the trajectory
        rmsd       = pid.parse_RMSD() #Get RMSG graph

        workdir = pid.ramdisk_out
        del pid
        gc.collect()

        #get intermolecular contacts (uses pytraj)
        hbonds = Contacts(projectID, mutantID, project)
        hbonds.computeContacts()

        cpptrajf10 = hbonds.getForwardContacts(10)
        cpptrajr10 = hbonds.getReverseContacts(10)
        cpptrajf20 = hbonds.getForwardContacts(5)
        cpptrajr20 = hbonds.getReverseContacts(5)
        cpptrajf50 = hbonds.getForwardContacts(2)
        cpptrajr50 = hbonds.getReverseContacts(2)

        pfolder = project["project_folder"]
        path_trajectory = f"{pfolder}/mutants/{mutantID}/outputs/{output_md}"

        #Get watersites (WaSiMap)
        water  = WaterMapper(projectID, mutantID, path_trajectory, 0.35, 0.006)
        mapdoc = db.dbtable_projects.find_one({"id_project": int(projectID)}, {"residuemap": 1, "objects": 1})
        wetspots = water.findWetSpots(mapdoc)

        #Prepare object for storing in DB
        db.dbtable_processed_data.delete_one(q) #delete if exists
        db.dbtable_processed_data.insert_one({
            **q,
            "pairwise_decomp": pairwise,
            "perresidue_decomp": perresidue,
            "deltag_total": delta_g['deltag_total'],
            "deltag_std": delta_g['deltag_std'],
            "best_frame": bestframe,
            "rmsd": rmsd,
            'water_ids': wetspots,
            'cpptraj_forward': cpptrajf10,
            'cpptraj_reverse': cpptrajr10,
            'cpptraj_forward20': cpptrajf20,
            'cpptraj_reverse20': cpptrajr20,
            'cpptraj_forward50': cpptrajf50,
            'cpptraj_reverse50': cpptrajr50
        })

        db.dbtable_mutants.update_one(q, {"$set": {
            'status': 'done',
            "status_vars.scavenger_progress_percentage": 100
        }})

        #Clear RAM
        if workdir and os.path.exists(workdir):
            shutil.rmtree(workdir)

        return mutantID

    except Exception as e:
        db.dbtable_mutants.update_one(q, {"$set": {
            'status': 'failed',
            "error": str(e)
        }})
        return None


class Scavenger:
    #Define output file name holding the H5 trajectory
    output_md = 'output_md.h5'

    def __init__(self, dbhostname):

        self.hostname = gethostname()
        self.DB = DymeDB(dbhostname)

        self.default_settings = self.DB.select_document("default_settings", {})

        self.cpus_per_energyprocess = 8
        self.available_cpus = get_available_cpus()
        self.max_workers = max(1, self.available_cpus // self.cpus_per_energyprocess)

        print(f"CPUs available: {self.available_cpus}")
        print(f"Parallel mutants: {self.max_workers}")

        self.process_loop(dbhostname)

    def claim_batch(self, batch_size):
        from datetime import datetime

        claimed = []
        for _ in range(batch_size):
            doc = self.DB.dbtable_mutants.find_one_and_update(
                {'status': 'ready_to_scavenge'},
                {'$set': {
                    'status': 'scavenging_local_queued',
                    'status_vars.scavenger_node': self.hostname,
                    'status_vars.scavenger_queue_time': datetime.now()
                }},
                sort=[('id_project', 1), ('mutantID', 1)],
                return_document=ReturnDocument.AFTER
            )
            if not doc:
                break
            claimed.append(doc)
        return claimed

    def process_loop(self, dbhostname):

        print("Starting global scavenger loop")

        while True:
            claimed = self.claim_batch(self.max_workers)

            if not claimed:
                print("No work. Sleeping 300s")
                time.sleep(300)
                continue

            print(f"Claimed: {[(d['id_project'], d['mutantID']) for d in claimed]}")

            tasks = [
                (
                    int(doc["mutantID"]),
                    int(doc["id_project"]),
                    dbhostname,
                    self.hostname,
                    self.cpus_per_energyprocess,
                    self.output_md
                )
                for doc in claimed
            ]

            with Pool(len(tasks)) as pool:
                pool.map(compute_energies_worker, tasks)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("dbhost", type=str, help="DyME main node hostname or IP")

    args = parser.parse_args()

    Scavenger(args.dbhost)