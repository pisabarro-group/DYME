#import mdanalysis as mda
import mdtraj as md
import parmed as parm

import sys
import os
from multiprocessing import Pool
from pymongo import ReturnDocument
import psutil as ps
import subprocess
#import json
import time
from ast import literal_eval
import argparse
#import uuid
from socket import gethostname


#File monitoring libs
#from watchdog.observers import Observer
#from watchdog.events import FileSystemEventHandler

#OWN
import Node #Includes Database Access Functions
from DymeTools import InputSystem, MMGBSA, WaterMapper, Contacts
from DymeDB import DymeDB


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
        slurm_total = int(slurm_cpt) * int(slurm_ntasks)
        return min(affinity_cpus, slurm_total) if affinity_cpus else slurm_total

    if slurm_cpt:
        return min(affinity_cpus, int(slurm_cpt)) if affinity_cpus else int(slurm_cpt)

    return affinity_cpus or (os.cpu_count() or 1)


def get_mutant_dirs(default_settings, mutID, projID):
    dirs = {}
    base_path = default_settings["hdd_path"] + default_settings["project_dir"] + "/" + str(projID)

    dirs["mutant"]  = f'{base_path}/mutants/{mutID}/'
    dirs["inputs"]  = f'{base_path}/mutants/{mutID}/inputs/'
    dirs["outputs"] = f'{base_path}/mutants/{mutID}/outputs/'
    dirs["ramdisk_in"]  = f'/mnt/ramdisk/{projID}/mutants/{mutID}/inputs/'
    dirs["ramdisk_out"] = f'/mnt/ramdisk/{projID}/mutants/{mutID}/outputs/'

    if not os.path.exists(dirs["ramdisk_in"]):
        os.makedirs(dirs["ramdisk_in"], exist_ok=True)

    if not os.path.exists(dirs["ramdisk_out"]):
        os.makedirs(dirs["ramdisk_out"], exist_ok=True)

    return dirs


def compute_energies_worker(args):
    import gc
    import shutil
    from datetime import datetime

    mutantID, projectID, dbhost, hostname, cpus_per_energyprocess, output_md = args

    db = DymeDB(dbhost)
    default_settings = db.select_document("default_settings", {})
    project = db.select_document("projects", {"id_project": projectID})
    paths = get_mutant_dirs(default_settings, mutantID, projectID)

    q = {'id_project': int(projectID), 'mutantID': int(mutantID)}
    timestart = int(time.time())
    workdir = None

    try:
        if "igb" in project["inputs"]:
            igbVal = project["inputs"]["igb"]
        else:
            igbVal = 2

        if "inp" in project["inputs"]:
            inpVal = project["inputs"]["inp"]
        else:
            inpVal = 1

        energ = "energy_gbsa"
        if "energy_pbsa" in project["analysis"]:
            energ = "energy_pbsa"

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

        newvalues = {"$set": {
            'status': 'scavenging_GBSA_pairwise',
            "status_vars.scavenger_node": hostname,
            "status_vars.scavenger_start_time": datetime.now(),
            "status_vars.scavenger_start_time_seconds": timestart,
            "status_vars.scavenger_progress_percentage": 0
        }}
        db.dbtable_mutants.update_one(q, newvalues)

        pid.genNCtrajectory(paths["mutant"])

        print("Running pairwise GBSA calculation on mutant " + str(mutantID), flush=True)
        cmd = codes["pairwise"]
        print(f'########\n Executing launch code:\n {cmd} \n####################')
        p = subprocess.Popen([f'{cmd}'], cwd=paths["ramdisk_in"], stdout=subprocess.PIPE, bufsize=2048, shell=True, executable='/bin/bash')
        print("Waiting for Pairwise process to complete")
        p.communicate()
        time.sleep(1)

        timenow = int(time.time()) - timestart
        newvalues = {"$set": {
            'status': 'scavenging_GBSA_perresidue',
            "status_vars.scavenger_elapsed": timenow,
            "status_vars.scavenger_progress_percentage": 40
        }}
        db.dbtable_mutants.update_one(q, newvalues)

        print("Launching per-residue energies now!")
        cmd = codes["perresidue"]
        print(f'########\n Executing launch code:\n {cmd} \n####################')
        p = subprocess.Popen([f'{cmd}'], cwd=paths["ramdisk_in"], stdout=subprocess.PIPE, bufsize=2048, shell=True, executable='/bin/bash')
        print("Waiting for Per-residue process to complete")
        p.communicate()
        time.sleep(1)

        print("##########FINISHED MMPBSA FOR Mutant " + str(mutantID) + " #############")
        time.sleep(2)

        anchorpoints = []
        for cluster in project["clusters"]:
            if cluster is not None:
                anchorpoints += cluster

        timenow = int(time.time()) - timestart
        newvalues = {"$set": {
            'status': 'scavenging_deltas_table',
            "status_vars.scavenger_elapsed": timenow,
            "status_vars.scavenger_progress_percentage": 80
        }}
        db.dbtable_mutants.update_one(q, newvalues)

        print("Collecting DeltaGs from MMPBSA outputs")
        delta_g = pid.parse_deltaG()
        gc.collect()

        print("Collecting Perrresidue data")
        perresidue = pid.parse_Perresidue()
        gc.collect()

        print("Collecting pairwise data")
        pairwise = pid.parse_Pairwise(anchorpoints)
        gc.collect()

        print("Collecting Best Frame")
        bestframe = pid.parse_BestFrame()
        gc.collect()

        print("Computing RMSD Data")
        rmsd = pid.parse_RMSD()
        gc.collect()

        workdir = pid.ramdisk_out
        del pid
        gc.collect()

        print("Computing contacts with cpptraj")
        hbonds = Contacts(projectID, mutantID, project)
        hbonds.computeContacts()

        print("Computing 10% Threshold")
        cpptrajf10 = hbonds.getForwardContacts(10)
        cpptrajr10 = hbonds.getReverseContacts(10)

        print("Computing 20% Threshold")
        cpptrajf20 = hbonds.getForwardContacts(5)
        cpptrajr20 = hbonds.getReverseContacts(5)

        print("Computing 50% Threshold")
        cpptrajf50 = hbonds.getForwardContacts(2)
        cpptrajr50 = hbonds.getReverseContacts(2)

        pfolder = project["project_folder"]
        path_trajectory = f"{pfolder}/mutants/{mutantID}/outputs/{output_md}"
        distance_threshold = 0.35
        persistence_threshold = 0.006
        water = WaterMapper(projectID, mutantID, path_trajectory, distance_threshold, persistence_threshold)

        print("Booting up water mapper")
        mapdoc = db.dbtable_projects.find_one({"id_project": int(projectID)}, {"residuemap": 1, "objects": 1})
        wetspots = water.findWetSpots(mapdoc)

        print("Done Scavenging.. saving to database")
        energydata = {
            'id_project': int(projectID),
            'mutantID': int(mutantID),
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
        }

        db.dbtable_processed_data.delete_one({'id_project': int(projectID), 'mutantID': int(mutantID)})
        db.dbtable_processed_data.insert_one(energydata)

        timenow = int(time.time()) - timestart
        timeend = int(time.time())
        newvalues = {"$set": {
            'status': 'done',
            "status_vars.scavenger_elapsed": timenow,
            "status_vars.scavenger_finish_time": datetime.now(),
            "status_vars.scavenger_finish_time_seconds": timeend,
            "status_vars.scavenger_progress_percentage": 100
        }}
        db.dbtable_mutants.update_one(q, newvalues)

        if workdir and os.path.exists(workdir):
            print(f'Clearing space on {workdir} - Removing workdir from ramdrive')
            shutil.rmtree(workdir)

        print(f"Finished Scavenging Energy tables of mutant {mutantID} of project {projectID}")
        return mutantID

    except Exception as e:
        print("Some error in " + str(mutantID) + " " + str(e))
        timenow = int(time.time()) - timestart
        newvalues = {"$set": {
            'status': 'failed',
            "status_vars.scavenger_elapsed": timenow,
            "status_vars.scavenger_progress_percentage": 0,
            "error": str(e)
        }}
        db.dbtable_mutants.update_one(q, newvalues)

        try:
            if workdir and os.path.exists(workdir):
                shutil.rmtree(workdir)
        except Exception:
            pass

        return None


class Scavenger():
    
    path          = ""
    projectID     = 0
    prmtop_file   = "receptor_ligand.prmtop"
    inpcrd_file   = "receptor_ligand.inpcrd"
    pdb_hydrated  = "receptor_ligand_wat.pdb"
    prmtop_hydrated  = "receptor_ligand_wat.prmtop"
    pdb_dry       = "receptor_ligand.pdb"
    pdb_mutated   = "original_mutated.pdb"
    pdb_original  = "original.pdb"
    output_md     = 'output_md.h5'
    
    cpus_required = {
            'energy_pairwise': 8,
            'energy_perresidue': 8,
            'energy_total': 1,
            'rmsd_averaged': 1,
            'rmsd_percarbon': 1,
            'bonds_hbonds': 1,
            'bonds_vdw': 1,
            'principal_component': 1,
            'water_track_interface': 1
        }
        
    #Scavenger Constructor
    def __init__(self, mutantID, projectID, operation, slurmQueue, count, dbhostname):
        
        self.instance_id     = 0
        self.projectID       = projectID
        self.datetime_start  = int(time.time())
        self.log             = []
        self.node_type       = "SCAVENGER"
        self.lictoken        = ""
        self.status          = "booting"
        self.slurmQueue      = slurmQueue
        self.hostname        = gethostname()
        self.DB              = DymeDB(dbhostname)
        
        self.default_settings = self.DB.select_document("default_settings",{})
        self.project          = self.DB.select_document("projects",{"id_project": self.projectID}) if self.projectID else None
        self.path             = ""
        if self.projectID:
            self.path = self.default_settings["hdd_path"] + self.default_settings["project_dir"] + "/" + str(projectID)
        self.executables      = "/dyme_base/backend/dyme/"
                
        self.cpus_per_energyprocess = 8
        self.available_cpus = get_available_cpus()
        self.max_workers = max(1, self.available_cpus // self.cpus_per_energyprocess)

        print(f"Scavenger configured with {self.cpus_per_energyprocess} CPUs per mutant")
        print(f"Detected {self.available_cpus} usable CPUs -> max parallel mutants: {self.max_workers}")

        if operation == "slurm":
            self.addPendings(count, self.projectID, dbhostname)

        elif operation == "process":
            if count:
                self.countPendings(self.projectID)
            elif mutantID and projectID:
                compute_energies_worker((
                    int(mutantID),
                    int(projectID),
                    dbhostname,
                    self.hostname,
                    self.cpus_per_energyprocess,
                    self.output_md
                ))
            else:
                self.processPendingsLocal(dbhostname)

        
    #Destructor
    def __exit__(self):
        print("Closing Scavenger Node")


    #Checks pending and creates SLURM jobs without updating database status
    def addPendings(self, count, id_project, dbhostname):  
        self.status = "scavenging"
        print("Scavenger Node Active / Starting Scavenger Checker")
        while(True):
            q = {'status': 'ready_to_scavenge', 'id_project': id_project}
            getpending = self.DB.dbtable_mutants.find(q)
            
            if count:
                c= len(list(getpending.clone()))
                print(f"\n Found {c} mutants pending to scavenge \n ")
                exit(0)
            
            if getpending is not None:
                for poll in getpending:

                    projectID = poll["id_project"]
                    mutantID  = poll["mutantID"]
                    print(f"Found pending mutant {mutantID} in project No. {projectID}!!")
                                        
                    dirs = self.getMutantDirs(mutantID, projectID)
                    
                    sbatch_content = """#!/bin/bash -l
#SBATCH --job-name=DYME_proj_"""+str(projectID)+"_mut_"+str(mutantID)+"""
#SBATCH --output="""+dirs["outputs"]+"""output_slurm.txt
#SBATCH --error="""+dirs["outputs"]+"""output_slurm_error.txt
#SBATCH --partition="""+self.slurmQueue+"""
#SBATCH --ntasks="""+str(self.cpus_per_energyprocess)+"""
#SBATCH --cpus-per-task=1

echo "Start date: $(date)"
source ~/.bashrc &
wait
conda init &
wait
conda activate dyme_scavenger &
wait
python """+self.executables+"Scavenger_slurm.py -d "+str(dbhostname)+" -e process -p "+str(projectID)+" -m "+str(mutantID)+""" &
wait
echo "End date: $(date)"
exit 0
"""
                    filename = dirs["inputs"]+"slurm.dyme"
                    with open(filename, 'w+') as f:
                        print(f"Writing to {filename}")
                        f.write(sbatch_content)
                    
                    try:
                        result = subprocess.run(['sbatch', filename], capture_output=True, text=True, check=True)
                        job_id = result.stdout.strip().split()[-1]
                        print("SLURM job (ID: {}) submitted successfully.".format(job_id))
                        q         = {'id_project': projectID, 'mutantID': mutantID}
                        newvalues = {"$set": { 'status': 'scavenging_on_queue' }}
                        self.DB.dbtable_mutants.update_one(q, newvalues)
                        print("Job submitted successfully!")
                    except subprocess.CalledProcessError as e:
                        print("Error submitting job:", e)
            else:
                print("Nothing to Scavenge.. sleeping 5 mins")
            time.sleep(300)
                
    
    def getMutantDirs(self, mutID, projID):
        return get_mutant_dirs(self.default_settings, mutID, projID)


    def countPendings(self, id_project=0):
        q = {'status': 'ready_to_scavenge'}
        if id_project:
            q['id_project'] = id_project

        c = self.DB.dbtable_mutants.count_documents(q)

        if id_project:
            print(f"\nFound {c} mutants pending to scavenge in project {id_project}\n")
        else:
            print(f"\nFound {c} mutants pending to scavenge across all projects\n")

        exit(0)


    def claimPendingBatch(self, batch_size, id_project=0):
        from datetime import datetime

        claimed = []

        for _ in range(batch_size):
            q = {'status': 'ready_to_scavenge'}
            if id_project:
                q['id_project'] = id_project

            doc = self.DB.dbtable_mutants.find_one_and_update(
                q,
                {
                    '$set': {
                        'status': 'scavenging_local_queued',
                        'status_vars.scavenger_node': self.hostname,
                        'status_vars.scavenger_queue_time': datetime.now(),
                        'status_vars.scavenger_progress_percentage': 0
                    }
                },
                sort=[('id_project', 1), ('mutantID', 1)],
                return_document=ReturnDocument.AFTER
            )

            if doc is None:
                break

            claimed.append(doc)

        return claimed


    def processPendingsLocal(self, dbhostname):
        print("Scavenger Node Active / Starting LOCAL Scavenger Dispatcher")

        while True:
            claimed = self.claimPendingBatch(self.max_workers)

            if not claimed:
                print("Nothing to scavenge. Sleeping 5 mins")
                time.sleep(300)
                continue

            claimed_pairs = [(int(doc["id_project"]), int(doc["mutantID"])) for doc in claimed]
            print(f"Claimed {len(claimed_pairs)} mutants: {claimed_pairs}")

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

            with Pool(processes=len(tasks)) as pool:
                results = pool.map(compute_energies_worker, tasks)

            print(f"Finished batch: {results}")
            print("Batch finished. Requesting a new batch...")


    #Kept for backwards compatibility. Worker path now uses compute_energies_worker()
    def compute_energies(self, mutantID, projectID, project, dbhost):
        return compute_energies_worker((
            int(mutantID),
            int(projectID),
            dbhost,
            self.hostname,
            self.cpus_per_energyprocess,
            self.output_md
        ))


    #Code to compute hbonding information of a single MD trajectory
    #Out: Stores hbonding information per MD trajectory in database
    def compute_hbonds(self, projectID, mutantID, mutantdir):
        pass
    
    
    #Code to compute VDW interactions from residues in MD
    #Out: Stores VDW interaction information per MD trajectory in database
    def compute_vdw(self, projectID, mutantID, mutantdir):
        pass    
    
    #Code to compute Proncipal component analysis
    #Out: Computes PCA of an MD trajectory, stores in DB
    def compute_pca(self, projectID, mutantID, mutantdir):
        pass    
    
    #Code to compute Contact Map of MD trajectory
    #Out: Builds a heatmap, contactmap of the MD trajectory
    def compute_contacts(self, projectID, mutantID, mutantdir):
        pass    
    
    #Code to compute Water tracking in the interface
    #Out: Somehow... try to do this reasonably easy.
    def compute_water_tracking(self, projectID, mutantID, mutantdir):
        pass
    
    
    
#MAIN
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='DYME Scavenger Node can queue analysis to SLURM or process ready_to_scavenge mutants locally in batches.'
    )
    parser.add_argument('-d', "--dbhost", type=str, help="Hostname or IP Address of the Main Node Docker instance", required=True, default="localhost")
    parser.add_argument('-p','--proj', help='DYME project ID', type=int, required=False, default=0)
    parser.add_argument('-m','--mut',  help='Mutant ID', type=int, required=False, default=0)
    parser.add_argument('-q','--que',  help='SLURM queue name. Default: bioinfp_cpu', default="bioinfp_cpu", required=False)
    parser.add_argument('-e','--ope',  help='Operation to perform: process|slurm. Default: process', default="process", required=False)
    parser.add_argument('-c','--count_only',  action=argparse.BooleanOptionalAction, help='Count pending trajectories only', default=False, required=False)
    args = vars(parser.parse_args())

    hostname   = args["dbhost"]
    mutantID   = args["mut"]
    projectID  = args["proj"]
    slurmQueue = args["que"]
    operation  = args["ope"]
    count      = args["count_only"]

    if operation not in ["process", "slurm"]:
        print("Invalid operation. Use process or slurm")
        exit(1)

    if operation == "process":
        if count:
            if projectID:
                print(f"Counting pending mutants for project {projectID}")
            else:
                print("Counting pending mutants across all projects")
        elif mutantID and projectID:
            print(f"Processing single mutant {mutantID} of project {projectID}")
        elif mutantID and not projectID:
            print("If you provide a mutantID, you must also provide a projectID")
            exit(1)
        elif projectID and not mutantID:
            print("ProjectID alone is not used for single-mutant mode. Provide both -p and -m, or neither for automatic batch mode.")
            exit(1)
        else:
            print("Processing ready_to_scavenge mutants across all projects")

    if operation == "slurm":
        if not projectID:
            print("SLURM mode requires a projectID with -p")
            exit(1)

        if count: 
            print(f"Counting pending mutants for project {projectID}")
        else:
            print(f"All pending mutants of project {projectID} will be sent to queue '{slurmQueue}'. This node should be able to execute sbatch")

    node = Scavenger(mutantID, projectID, operation, slurmQueue, count, hostname)