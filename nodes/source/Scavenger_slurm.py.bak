# -*- coding: utf-8 -*-
"""
DYME - Dynamic Mutagenesis Engine v0.1

File:           Scavenger_slurm.py
Description:    Mutagenesis Generator Class

Purpose:        -Provides functions to scavenge data from trajectories
                 This version of the scavenger deploys pending jobs using the SLURM workload manager 

Provides:       -class Scavenger()

Author:     
Pedro Manuel Guillem Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>
Structural Bioinformatics Laboratory - BIOTEC - Pisabarro Group
Technische Universität Dresden

Mar 2023 - Built the whole thing... >)
May 2023 - We have issues with failing file handles when the process queue is too long. Opt for slurm... I Need more time to figure out this one.
May 2023 - Built this version of the Scavenger... runs once.. we deploy to slurm

"""

#import mdanalysis as mda
import mdtraj as md
import parmed as parm

import sys
import os
from multiprocessing import Pool, current_process, cpu_count, Process, Queue
import psutil as ps
import subprocess
#import json
import time
from ast import literal_eval
import argparse
#import uuid
from socket import gethostname
import time


#File monitoring libs
#from watchdog.observers import Observer
#from watchdog.events import FileSystemEventHandler

#OWN
import Node #Includes Database Access Functions
from DymeTools import InputSystem, MMGBSA, WaterMapper, Contacts
from DymeDB import DymeDB

class Scavenger():
    
    path          = "" #This is the path to the project folder - Must be set in the constructor
    projectID     = 0 #This is the ID of the project - Must be set in the constructor
    prmtop_file   = "receptor_ligand.prmtop" #this is the OpenMM input in all mutants
    inpcrd_file   = "receptor_ligand.inpcrd" #This is the OpenMM input in all mutants too
    pdb_hydrated  = "receptor_ligand_wat.pdb" #this is the hydrated and equilibrated template in all mutants
    prmtop_hydrated  = "receptor_ligand_wat.prmtop" #this is the hydrated and equilibrated template in all mutants
    pdb_dry       = "receptor_ligand.pdb" #This is how the template will lokk like in every mutant
    pdb_mutated   = "original_mutated.pdb" #This is how the template will lokk like in every mutant
    pdb_original  = "original.pdb" #This is how the template will lokk like in every mutant
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
        
        self.instance_id     = 0   #Unique node ID in the swarm
        self.projectID       = projectID
        self.datetime_start  = int(time.time())     #Date of creation
        self.log             = []    #Log list
        self.node_type       = "SCAVENGER"    #type of Node
        self.lictoken        = ""    #License
        self.status          = "booting"    #Status of node        
        self.slurmQueue      = slurmQueue
        self.hostname        = gethostname()
        self.DB = DymeDB(dbhostname)
        
        self.default_settings = self.DB.select_document("default_settings",{})
        self.project          = self.DB.select_document("projects",{"id_project": self.projectID})
        self.path             = self.default_settings["hdd_path"]+self.default_settings["project_dir"]+"/"+str(projectID) #Get DYME default directory in database
        self.executables      = "/dyme_base/backend/dyme/"
                
        #Compute CPU availability
        #self.max_workers = cpu_count()/self.cpus_per_energyprocess
        self.max_workers = 8
        self.cpus_per_energyprocess = 8


        #Add to SLurm Always enqueue new mutants
        if operation == "slurm":
            self.addPendings(count, self.projectID, dbhostname)

        #Process individual mutant of a project id
        if operation == "process":
            self.compute_energies(mutantID, projectID, self.project, dbhostname)


        
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
            
            if getpending is not None: #if DB returns a pending mutant
                for poll in getpending:

                    #Get values of record
                    projectID = poll["id_project"]
                    mutantID  = poll["mutantID"]
                    print(f"Found pending mutant {mutantID} in project No. {projectID}!!")
                                        
                    #ENQUEUE EACH ANALYSIS ROUTINE IN SLURM
                    dirs = self.getMutantDirs(mutantID, projectID)
                    
                    #Build SBATCH file for mutant
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
                    #A random filename
                    filename = dirs["inputs"]+"slurm.dyme"
                    with open(filename, 'w+') as f:
                        print(f"Writing to {filename}")
                        f.write(sbatch_content)
                    
                    try:
                        #Add to SLURM
                        result = subprocess.run(['sbatch', filename], capture_output=True, text=True, check=True)
                        job_id = result.stdout.strip().split()[-1]  # Extract the job ID from the output
                        print("SLURM job (ID: {}) submitted successfully.".format(job_id))
                        #Update mutant status to "scavenging"
                        q         = {'id_project': projectID, 'mutantID': mutantID}
                        newvalues = {"$set": { 'status': 'scavenging_on_queue' }}
                        self.DB.dbtable_mutants.update_one(q, newvalues)
                        print("Job submitted successfully!")
                    except subprocess.CalledProcessError as e:
                        print("Error submitting job:", e)
            else:
                print("Nothing to Scavenge.. sleeping 5 mins")
            time.sleep(300)
                
    
    #Quickie... we don't wanna do this everywhere . Mar 7 2022
    def getMutantDirs(self, mutID, projID):
        dirs = {}
        self.path = self.default_settings["hdd_path"]+self.default_settings["project_dir"]+"/"+str(projID)
        dirs["mutant"]  = f'{self.path}/mutants/{mutID}/'
        dirs["inputs"]  = f'{self.path}/mutants/{mutID}/inputs/'
        dirs["outputs"] = f'{self.path}/mutants/{mutID}/outputs/'   
        dirs['ramdisk_in']  = f'/mnt/ramdisk/{projID}/mutants/{mutID}/inputs/' #Fixed Oct 2024 - Include project id in path
        dirs['ramdisk_out'] = f'/mnt/ramdisk/{projID}/mutants/{mutID}/outputs/' #Fixed Oct 2024 - Same
        
        if not os.path.exists(dirs['ramdisk_in']):
                os.makedirs(dirs['ramdisk_in'])
                
        if not os.path.exists(dirs['ramdisk_out']):
                os.makedirs(dirs['ramdisk_out'])
        
        return dirs        
    
    
        
    #Code to compute pairwise energies and other scavenging
    #Out: Stores pairwise energy and scavenging maps in database
    def compute_energies(self, mutantID, projectID, project, dbhost): #THIS MEANS ALL ENERGIES, ALSO PERRESIDUE    
            import gc
            import shutil
            
            paths = self.getMutantDirs(mutantID, projectID)
            #print(paths)
            
            #Set GBSA igb
            if "igb" in project["inputs"]:
                igbVal = project["inputs"]["igb"] # ADDED FEB 21 2024 - Enables computing energies with igb 2 or 8 (Default is 2)
            else:
                igbVal = 2
            
            #OCT - 2024 - Add inp    
            if "inp" in project["inputs"]:
                inpVal = project["inputs"]["inp"]
            else:
                inpVal = 1
            
            #Choose GBSA or PBSA
            energ = "energy_gbsa"
            if "energy_pbsa" in project["analysis"]:
                energ = "energy_pbsa"
            
            #Pending - Set the right number of steps on MMGBSA!!!!!
            pid = MMGBSA(mutantID=int(mutantID), outPath=paths['mutant'], interval=30, igb=igbVal, inp=inpVal, compute_mode=energ)
            pid.setRamDisk(paths['ramdisk_in'], paths['ramdisk_out']) #TODO - Make this universal, needs root to create ramdisk for MMPBSA in Scavenger nodes? (or just save to tmp)
            pid.makeInputs()
            pid.writeInputs()
            codes = pid.launchCodes(self.cpus_per_energyprocess)
            
            try:
                #Create suitable trajectory from HF5
                #update Mutant
                from datetime import datetime
                from DymeDB import DymeDB
                db = DymeDB(dbhost) #New mongodb instance.. from the fork..
                
                #UPDATE STATUS
                timestart = int(time.time())
                q         = {'id_project': projectID, 'mutantID': mutantID}
                newvalues = {"$set": { 'status': 'scavenging_GBSA_pairwise', "status_vars.scavenger_node": self.hostname, "status_vars.scavenger_start_time": datetime.now(), "status_vars.scavenger_start_time_seconds": timestart, "status_vars.scavenger_progress_percentage": 0}}
                db.dbtable_mutants.update_one(q, newvalues)
                
                    
                pid.genNCtrajectory(paths['mutant'])
                
                print("Running pairwise GBSA calculation on mutant "+ str(mutantID), flush=True)
                cmd = codes['pairwise']
                print(f'########\n Executing launch code:\n {cmd} \n####################')
                #TODO - Figure out where to find GGPBSA in any server this is installed into, static paths will not work unless dockerized
                p = subprocess.Popen([f'{cmd}'], cwd=paths['ramdisk_in'], stdout=subprocess.PIPE, bufsize=2048, shell=True, executable='/bin/bash')
                print("Waiting for Pairwise process to complete")
                p.communicate()
                time.sleep(1)
                
                #UPDATE STATUS
                timenow = int(time.time())-timestart
                
                q         = {'id_project': projectID, 'mutantID': mutantID}
                newvalues = {"$set": { 'status': 'scavenging_GBSA_perresidue', "status_vars.scavenger_elapsed": timenow, "status_vars.scavenger_progress_percentage": 40}}
                db.dbtable_mutants.update_one(q, newvalues)
                
                print("Launching per-residue energies now!")                                
                cmd = codes['perresidue']
                print(f'########\n Executing launch code:\n {cmd} \n####################')
                p = subprocess.Popen([f'{cmd}'], cwd=paths['ramdisk_in'], stdout=subprocess.PIPE, bufsize=2048, shell=True, executable='/bin/bash')
                print("Waiting for Per-residue process to complete")
                p.communicate()
                time.sleep(1)
                
                

                    
                print("##########FINISHED MMPBSA FOR Mutant "+str(mutantID)+" #############")
                time.sleep(2)
                
                
                
                ##################################################################################################
                #Get anchorpoints for project
                anchorpoints = []
                for cluster in self.project['clusters']:
                    if cluster is not None:
                        anchorpoints += cluster
                
                timenow = int(time.time())-timestart
                q         = {'id_project': projectID, 'mutantID': mutantID}
                newvalues = {"$set": { 'status': 'scavenging_deltas_table', "status_vars.scavenger_elapsed": timenow, "status_vars.scavenger_progress_percentage": 80}}
                                
                db.dbtable_mutants.update_one(q, newvalues)
                
                #EXTRACT DATA INTO DATABASE
                
                #1. DeltaG total of System (returns dictionary of deltaG tot and deltag std)
                print("Collecting DeltaGs from MMPBSA outputs")
                delta_g      = pid.parse_deltaG()
                gc.collect()
                #2. Perresidue Energies
                print("Collecting Perrresidue data")
                perresidue   = pid.parse_Perresidue()                                
                gc.collect()
                #3. Pairwise Energy
                print("Collecting pairwise data")
                pairwise    = pid.parse_Pairwise(anchorpoints) #Watch out - Only relevant anchorpoint data is taken.
                gc.collect()
                #4. Get best frame (from HDF5 file), write wat and dry PDBs of best frame to output
                print("Collecting Best Frame")
                bestframe    = pid.parse_BestFrame()  
                gc.collect()
                #5. Get RMSD of Mutant
                print("Computing RMSD Data")
                rmsd         = pid.parse_RMSD()
                gc.collect()
                
                #Close object just in case
                workdir = pid.ramdisk_out
                del pid
                gc.collect() #Collect garbage after previous step
                
                #6. Get HBONDS of Mutant with CPPTRaj/PyTraj
                print("Computing contacts with cpptraj")
                hbonds           = Contacts(projectID, mutantID, self.project)
                hbonds.computeContacts()
                print("Computing 10% Threshold")
                cpptrajf10         =  hbonds.getForwardContacts(10) #Get Forward contacts
                cpptrajr10         =  hbonds.getReverseContacts(10) #Get Reversed Contacts
                print("Computing 20% Threshold")
                cpptrajf20         =  hbonds.getForwardContacts(5) #Get Forward contacts
                cpptrajr20         =  hbonds.getReverseContacts(5) #Get Reversed Contacts
                print("Computing 50% Threshold")                
                cpptrajf50         =  hbonds.getForwardContacts(2) #Get Forward contacts
                cpptrajr50         =  hbonds.getReverseContacts(2) #Get Reversed Contacts

                #7.Get waters 
                pfolder               = self.project['project_folder']
                path_trajectory       = f"{pfolder}/mutants/{mutantID}/outputs/{self.output_md}"
                distance_threshold    = 0.35 #Distance around atoms of the sidechains
                persistence_threshold = 0.006  #Percentage of frames for a water to be relevant with speed near 0
                water                 = WaterMapper(projectID, mutantID, path_trajectory, distance_threshold, persistence_threshold)
                #water.loadTrajectory()
                water_atomids         = {}
                print("Booting up water mapper")
                map                   = db.dbtable_projects.find_one({"id_project": int(projectID)},{"residuemap": 1, "objects": 1})
                wetspots              = water.findWetSpots(map)
                
                #Delete this two before production
                print("Done Scavenging.. saving to database")
                
                #Insert all this into DB in per-mutant profile books                
                energydata = {'id_project': projectID, 'mutantID': mutantID, "pairwise_decomp": pairwise, "perresidue_decomp": perresidue, "deltag_total" : delta_g['deltag_total'], "deltag_std": delta_g['deltag_std'], "best_frame": bestframe, "rmsd": rmsd, 'water_ids': wetspots, 'cpptraj_forward': cpptrajf10, 'cpptraj_reverse': cpptrajr10,'cpptraj_forward20': cpptrajf20, 'cpptraj_reverse20': cpptrajr20,'cpptraj_forward50': cpptrajf50, 'cpptraj_reverse50': cpptrajr50}
                db.dbtable_processed_data.delete_one({'id_project': int(projectID), 'mutantID': int(mutantID)}) #Prevent having to manually delete previously scavenged results
                db.dbtable_processed_data.insert_one(energydata) #insert scavenger dictionary in the db
                
                #update mutant on table
                timenow = int(time.time())-timestart
                timeend = int(time.time())
                q         = {'id_project': projectID, 'mutantID': mutantID}
                newvalues = {"$set": { 'status': 'done', "status_vars.scavenger_elapsed": timenow, "status_vars.scavenger_finish_time": datetime.now(), "status_vars.scavenger_finish_time_seconds": timeend, "status_vars.scavenger_progress_percentage": 100}}
                db.dbtable_mutants.update_one(q, newvalues)
                #Delete work directory from ramdrive
                print(f'Clearing space on {workdir} - Removing workdir from ramdrive')
                shutil.rmtree(f'{workdir}')
                
                
                print(f"Finished Scavenging Energy tables of mutant {mutantID} of project {projectID}")
            except Exception as e: 
                print("Some error in " + str(mutantID) +" "+str(e))
                db = DymeDB(dbhost) #New mongodb instance.. from the fork..                
                timenow = int(time.time())-timestart
                newvalues = {"$set": { 'status': 'failed', "status_vars.scavenger_elapsed": timenow, "status_vars.scavenger_progress_percentage": 0, "error": str(e)}}
                db.dbtable_mutants.update_one(q, newvalues)


    
    #Code to compute hbonding information of a single MD trajectory
    #Out: Stores hbonding information per MD trajectory in database
    def compute_hbonds(self, projectID, mutantID, mutantdir):
        #t = md.load(f'{mutantdir}/outputs/{self.output_md}', top=f'{mutantdir}/inputs/{prmtop_hydrated}') #Load mutant trajectory and prmtop file
        #hbonds = md.baker_hubbard(t, periodic=False, sidechain_only=True, freq=0.1, exclude_water=False)  #TODO- Se freq to the threshold in the dyme GUI
        #label = lambda hbond : '%s -- %s' % (t.topology.atom(hbond[0]), t.topology.atom(hbond[2])) #Count hbonds with a quickie lambda function
        
        #lastPosInFirstChain = "" #Get from project['residuemap']
        
        #cont = 0
        #for hbond in hbonds:
          #print(label(hbond))
        #  atom1 = t.topology.atom(hbond[0])
        #  atom2 = t.topology.atom(hbond[2])
          
        #  if atom1.residue.index+1 < lastPosInFirstChain and atom2.residue.index+1 < lastPosInFirstChain:
             #Hbonds between sidechains of the same chain... skip
        #     continue
         # elif atom1.residue.index+1 > lastPosInFirstChain and atom2.residue.index+1 > lastPosInFirstChain:
             #Hbonds between sidechains of the same chain... skip
        #     continue
        #  else:
              #Hbonds between both molecular objects!!.. these we are interested in (for now)
              #print(str(atom1.residue.index+1)+atom1.residue.name+"-->"+str(atom2.residue.index+1)+atom2.residue.name)
              #print(label(hbond))
         #     cont +=1
              
        #Build hbond counter & maps
        #Insert hbond map into database (use projectID and mutantID)
        #update scavenging status for this process on this mutant     
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

    #Parse Arguments
    parser = argparse.ArgumentParser(description='DYME Scavenger Node. Queues analysis scavenging data from trajectories using a SLURM CPU cluster')
    parser.add_argument('-d', "--dbhost", type=str, help="Hostname or IP Address of the Main Node Docker instance", required=True, default="localhost")
    parser.add_argument('-p','--proj', help='DYME project ID', type=int, required=False, default=0)
    parser.add_argument('-m','--mut',  help='Mutand ID', type=int, required=False, default=0)
    parser.add_argument('-q','--que',  help='SLURM queue name. Default: bioinfp_cpu', default="bioinfp_cpu", required=False)
    parser.add_argument('-e','--ope',  help='Operation to perform: get pending jobs and fill slurm queue, or process a mutant (options are: process|slurm). The default behavior is to process', default="process", required=False)
    parser.add_argument('-c','--count_only',  action=argparse.BooleanOptionalAction, help='Count pending trajectories only', default=False, required=False)
    args = vars(parser.parse_args())

    #TODO: Check inputs are numbers when they should be numbers, exit otherwise
    #Dunno... get fancy.. check id the SLURM queue exists.. check if machine has SLURM installed, etc etc etc... para nota

    #Get mutantiD and project number
    hostname   = args["dbhost"]
    mutantID   = args["mut"]
    projectID  = args["proj"]
    slurmQueue = args["que"]
    operation  = args["ope"]
    count      = args["count_only"]
        
    #We set purposely this to the default option, so it prevents launching a process without mutantID and projectID
    if count:
        operation = "slurm"
    
    #Check mutantID    
    if operation == "process":
        if mutantID == 0 or projectID == 0:
            print("You must set mutantID and projectID if you'd like to run a process. Use options -p and -m")
            exit(0)
        else:
            print(f"Queueing mutant {mutantID} of project {projectID}")
    
    #Check mutantID    
    if operation == "slurm":
        print(f"All pending mutants will be sent to queue '{slurmQueue}'. This node should be able to execute sbatch")
    
    node = Scavenger(mutantID, projectID, operation, slurmQueue, count, hostname)
