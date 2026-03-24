
# -*- coding: utf-8 -*-
"""
DYME - Dynamic Mutagenesis Engine v0.1

File:           MD.py
Description:    MD Engine class

Purpose:        -Provides a continuous MD engine
                (WARNING: THIS WILL ONLY RUN ON SERVER EQUIPPED WITH AT LEAST 1 GPU CARD)

Provides:       -class MD()



Jan 2023 -  Added Database Support 
            Added Runner function
            Added DB Query for new mutant function
            Added OpenMM custom script
            Added MDparams dict

Mar 2023 -  Added DB Reporter cappability during MD
            Added AmberSelector Solver for any project
          
          
          
Author:     
Pedro Manuel Guillem Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>
Structural Bioinformatics Laboratory - BIOTEC - Pisabarro Group
Technische Universität Dresden          
            
@author: pegu906a
           
"""


from openmm.app import *
from openmm import *
from openmm.unit import *
 
import sys
import os
import re
import multiprocessing as mp
import psutil as ps
import subprocess, getpass
import json
import time
from ast import literal_eval
from socket import gethostname
import h5py 
from os.path import exists
from mdtraj.reporters import HDF5Reporter #Load MDtraj Reporter bindings
from parmed.openmm import StateDataReporter as ParmedStateReporter
import argparse


#Ouw Own
import Node #Includes Database Access Functions
from DymeTools import InputSystem
from dbreporter import DYMEReporter as DYMEReporter
from DymeDB import DymeDB

 #MUTANT DEPLOYMENT ROUTINE
 #1- Get a list of GPUnumber pending mutants and assign to self
     #ask gpu number
     #request pending mutant dict
     #update status to processing
     #save mutant list to temp or iterate
     
 #2- Generate Tleap Files for each mutant and create mutant directory
 #3- Generateeach mutant pdb inside mutant directory
 #4- Run TLEAP to generate mutant inputs
 
 #5- RunOpenMM
 
 #THIS CODE WILL ONLY RUN IF THE SERVER HAS GPU CARDS!!
 ###############################################################################
 
class MD():
    
    md_params = {
        "output_path": "",
        "mutantID":  "",
        "projectID": "",
        "projectName": "",
        "platform":  "",
        "precision": "",
        "prmtop":    "",
        "inpcrd":    "",
        "ewaldTol": 0.0005,
        "nonbondedmethod": "",
        "cutoff":    "",
        "constraints":"",
        "constraintTolerance": 0.000001,
        "ensemble": "",
        "friction":   "",
        "temperature": "",
        "pressure": "",
        "barostatInterval": "",
        "dt":        "",
        "steps": "",
        "equilibrationSteps": "",
        "totalframes": ""
    }        
    
    def __init__(self, dbhostname, reusegpus):
        
        #DB object comes from Node.Node
        #AMPQ object comes from Node.Node
        #Register Node.Node default vars
        self.instance_id     = 0   #Unique node ID in the swarm
        self.datetime_start  = int(time.time())     #Date of creation
        self.log         = []    #Log list
        self.node_type   = "MD"    #type of Node
        self.lictoken    = ""    #License
        self.status      = "booting"    #Status of node        
        self.reusegpus   = reusegpus
        self.gpus        = self.get_free_gpus() #TODO- Detect if Server doesn't have GPUs, and exit if so
        #Check if system has GPUs for MD
        if len(self.gpus) == 0:
            exit("ERROR: MD Node can not start on a machine without GPU hardware")
        self.hostname = gethostname()
        self.DB = DymeDB(dbhostname)
        self.dbhostname = dbhostname
        
        #Set input/output dir of the current project
        print("Booting up MD node on DYME")
        self.status      = "idle" #Status of node        
        print("##############################################")
        print("MD node online - Ready to process DYME mutants")
        print("##############################################")
        
    
    #Uses ObjectMap and ResidueMap of project to compute an Amber selector mask for each molecular object
    #This is used for ParmEd to split the prmtop complex in ligand-receptor files
    #MMPBSA requires both files
    def buildSelectors(self, project):
        rmap    = project["residuemap"]
        robject = project["objects"]
        #iterate residue map to build ligand and receptor selector

        nonmutableobjs = []

        selector = {}
        for obj in robject:
            for cha in obj['chains']:
                #print(cha)
                chain = cha['key']
                res = []
                
                for residue in rmap[chain]:
                    if residue != None: #Some empty residues may have come in the map..ignore
                        res.append(residue['resno_NGL']) #list of residue positions post-amber.. not the orig PDB
                #TODO - support more than 2 molecular objects in the selector
                
                #IMPORTANT - YOU HAD TO PURPOSELY INCREASE THE LAST NUMBER IN THE SELECTOR FOR THE
                #RECEPTOR - PARMED IS ADDING A NH CAP AT THE END AFTER THE ZINCS, WHICH IS FIXED BY INCREASING
                #THE SELECTOR RANGE TO A NUMBER HIGHER THAN THE LAST RESIDUE OF THE MUTABLE OBJECT.
                
                #THIS MIGHT NOT WORK IF THE SECOND CHAIN IS NOT THE MUTABLE OBJECT, IT NORMALLY IS
                
                if obj['mutable'] == True: #ligand is always the mutable object
                    sel = f':{res[0]}-{res[-1]}' #amber selector string--currently supports only 2 objects
                    print(f'Computing ligand prmtop using selector {sel} from {len(res)}')
                    print(f'got chain {chain}')
                    selector['ligand'] = sel
                else:
                    print(f'got non-mutable chain {chain}')
                    nonmutableobjs.append(res)
                    #sel = f':{res[0]}-{res[-1]}' #amber selector string--currently supports only 2 objects
                    #print(f'Computing prmtop using selector {sel} from {len(res)}')
                    #selector['receptor'] = sel
                    
        #Pedro - Modified this code to work with DNA (usually 3 objects, 1 mutable protein and 2 DNA strands)
        # You added the residue collection per chain to nonmutableobjects
        print(nonmutableobjs) 
        #Depending on how many non-mutable objects there are, build the selector based on the first residue after the mutable, and the last ont he pdb
        if len(nonmutableobjs) > 1:
            #For more than one non mutable object
            ini = nonmutableobjs[0] #first non mutable
            end = nonmutableobjs[-1]  #last non mutable
            sel = f':{ini[0]}-{end[-1]}'
        else: 
            #for one remaining non mutable object
            res = nonmutableobjs[0] #only one remaining non mutable... first and last items are on the same object
            sel = f':{res[0]}-{res[-1]}'
        print(f'Computing receptor prmtop using selector {sel}')
        selector['receptor'] = sel
        print(f"Selectors were built: {selector}")
        return selector
            
       
    #Run Node operations
    def run(self):
        
        while(True):
            
            self.gpus = self.get_free_gpus()
            totgpus = self.gpus
            
            if len(self.gpus) < 1:
                print(f'All GPUs are busy.. waiting -> says '+self.hostname)
            else:
                print("Starting MD computing jobs")
                print(f'System has {totgpus} gpus free')
            
                #get one pending mutant per local GPU
                for gpu in self.gpus:
                    #get a pending mutant    
                    #print(self.get_free_gpus())
                    print(f'Polling a mutant for gpu {gpu}')
                    
                    projid, mutantID, mutantdict = self.queryPendingMutant() #Fetch a pending mutant to process
                    if mutantID is not None:
                        print(f'Got mutantID {mutantID} from project ID {projid}')
                        print(f'Building system for mutant {mutantID}')
                        
                        #gather project and system data
                        default_settings = self.DB.select_document("default_settings",{})
                        projectdata      = self.DB.select_document("projects", {"id_project": projid})
                        path             = default_settings["hdd_path"]+default_settings["project_dir"]+"/"
                        DymeSystem       = InputSystem(path, projid) #From DymeTools
                        
                        if type(mutantdict) is dict:
                            mutantdict = [mutantdict]
                            
                        #Create Tleap Params for mutant
                        tleapDict = DymeSystem.buildLeapDict(projid, path, mutantID, projectdata)
                        
                        #Create Mutant original.pdb for mutantID with modeller
                        DymeSystem.buildMutantFromWildType(mutantdict, mutantID)
                        
                        #Create folders, inputs and files for this mutant
                        sel = self.buildSelectors(projectdata) #get mutant's object selectors
                        DymeSystem.createTleapScriptandInputs(tleapDict,mutantID,sel) #Added support for generating ligand/receptor prmtop
                        #print(sel)
                        #Build OpenMM params dict for mutant
                        
                        #This feature was added later. Must check if existing projects have it.
                        if "totalframes" in projectdata["simulation"]:
                            totalframes = projectdata["simulation"]["totalframes"]
                        else:
                            totalframes = 1000
                        
                        md_params = {
                            "output_path":       path,
                            "mutantID":          int(mutantID),
                            "projectID":         str(projid),
                            "projectName":       projectdata["project_name"],
                            "platform":          projectdata["simulation"]["platform"],
                            "precision":         projectdata["simulation"]["precision"],
                            "prmtop":            "receptor_ligand_wat.prmtop",
                            "inpcrd":            "receptor_ligand_wat.inpcrd",
                            "ewaldTol":           float(projectdata["simulation"]["ewaldTol"]),
                            "nonbondedmethod":    "PME",
                            "cutoff":             projectdata["simulation"]["cutoff"],
                            "constraints":        projectdata["simulation"]["constraints"],
                            "constraintTolerance": projectdata["simulation"]["constraintTol"],
                            "ensemble":           projectdata["simulation"]["ensemble"],
                            "friction":           projectdata["simulation"]["friction"],
                            "temperature":        projectdata["simulation"]["temperature"],
                            "pressure":           projectdata["simulation"]["pressure"],
                            "barostatInterval":   projectdata["simulation"]["barostatInterval"],
                            "dt":                 projectdata["simulation"]["dt"],
                            "steps":              projectdata["simulation"]["steps"],
                            "equilibrationSteps": projectdata["simulation"]["equilibrationSteps"],
                            "totalframes":        totalframes
                        }
                        
                        #Launch Mutant in a GPU
                        p = mp.Process(target=self.runMD_fromAmber, args=(md_params,gpu,self.dbhostname,))
                        p.start()                                        
                    else:
                        print(f'Database has no pending mutants.. waiting')
                        
                print("Finished loading all GPUs.. waiting 60 seconds for some jobs to complete") #THis is temporary.. the idea is to make it responsive to GPUS getting free        
            time.sleep(60)
    
    
    def queryPendingMutant(self):       
        #Select a pending mutant
        #q = {'mutantID': 2, 'id_project': self.idproject}
        #q = {"status": "pending", 'id_project': self.idproject}
        q = {"status": "pending"}
        poll = self.DB.dbtable_mutants.find_one(q)
        if poll is not None:
            #Update mutant to "processing"
            q = {'id_project': poll['id_project'], 'mutantID': poll['mutantID']}
            newvalues = { "$set": { 'status': 'processing' } } #SET MUTANT TO PROCESSING - LOCK, SO NO OTHER MD NODES GET IT AGAIN
            self.DB.dbtable_mutants.update_one(q, newvalues)
            return [poll['id_project'], poll['mutantID'], poll['mutant']]
        else:
            return [None, None, None]
    
            
    def pollMDprogress(self, id_process):
        pass
    
    def reportMDprogress(self, mutantID, query):
        pass
    
    def runMD_fromCheckpoint(self):
        pass
                 
    
    def runMD_fromAmber(self, md_params, deviceindex, dbhostname):
        #MD_PARAMS template is stored in a class variable       
        #sys.stdout = open(str(os.getpid()) + ".out", "w")
        try:
            import time
            stdout = sys.stdout
            
            nonbondedMethod = PME
            nonbondedCutoff = float(md_params['cutoff'])*nanometers
            ewaldErrorTolerance = 0.0005
            constraints = HBonds
            rigidWater = True
            constraintTolerance = 0.000001
            platform = Platform.getPlatformByName(md_params['platform'])
            project_id = int(md_params["projectID"])
            mutantID = int(md_params["mutantID"])
            totalframes = int(md_params["totalframes"])
            
            #output name
            output_path = md_params["output_path"]+"/"+md_params["projectID"]+"/mutants/"+str(md_params["mutantID"])+"/outputs/"
            input_path  = md_params["output_path"]+"/"+md_params["projectID"]+"/mutants/"+str(md_params["mutantID"])+"/inputs/"
            
            #Check if output directory exists
            if not os.path.exists(output_path):
                os.makedirs(output_path)
                    
            output_name = 'output_md'
            checkpoint_name = 'output_checkpoint'
            output_textreporter = 'output_process.txt'
            
            print("Staring MD Node on Mutant "+str(md_params["mutantID"])+" of Project "+str(md_params["projectID"]))
            
            platform = Platform.getPlatformByName(md_params['platform']) #Use GPUs to compute
            if md_params['platform'] == "CUDA":
                #platformProperties = {'Precision': md_params['precision']} 
                #platformProperties = {'Precision': 'single', "DeviceIndex": str(deviceindex)}
                platformProperties = {'Precision': str(md_params['precision']), "DeviceIndex": str(deviceindex)} 
            else:
                #This is for supporting AMD and CPU in the future... not super tested tho
                pass    
            
            print("Loading MD File Inputs")
            prmtop = AmberPrmtopFile(input_path+md_params["prmtop"]) #Built by Tleap, read from project folder
            inpcrd = AmberInpcrdFile(input_path+md_params["inpcrd"]) #Built by Tleap
            print("Files Loaded... creating system")
            
            #Create System - Make sure you are launching well here... 
            #system = prmtop.createSystem(nonbondedMethod=PME, nonbondedCutoff=md_params["cutoff"]*nanometer, constraints=md_params["constraints"], rigidWater=True, ewaldErrorTolerance=md_params["ewaldTol"])
            system = prmtop.createSystem(nonbondedMethod=nonbondedMethod, nonbondedCutoff=nonbondedCutoff, constraints=constraints)
            
                                
            print("System created")
            integrator = LangevinMiddleIntegrator(int(md_params["temperature"])*kelvin, 1.0/picosecond, int(md_params["dt"])*femtoseconds) #Create Langevin Integrator - Collision frequency 1ps-1, 2 femtosecond steps at 300 kelvin
            integrator.setConstraintTolerance(constraintTolerance)
            
            print("Booting up Simulation")
            simulation = Simulation(prmtop.topology, system, integrator,  platform, platformProperties) #Build Simulation object with amber topology as source
            simulation.context.setPositions(inpcrd.positions) #Set starting positions from Amber file
            
            print("Insert Amber INPCRD object into simulation")
            if inpcrd.boxVectors is not None:
                simulation.context.setPeriodicBoxVectors(*inpcrd.boxVectors)
            
            print("Minimizing System")
            simulation.minimizeEnergy() #Minimize untill system converges
            
            print('Equilibrating System')
            
            #simulation.context.setVelocitiesToTemperature(int(md_params["temperature"])*kelvin)
            #simulation.step(int(md_params["equilibrationSteps"]))
            
            #PEDRO 2024 - NVT warmup first
            print('Warming up the system...')
            simulation.context.setVelocitiesToTemperature(5*kelvin)
            T = int(int(md_params["temperature"])/60)
            mdsteps = int(md_params["equilibrationSteps"])
            print(f'Executing 60 increments of {T} Kelvin till reaching {md_params["temperature"]} Kelvin, over {mdsteps} steps')
            for i in range(60):
              simulation.step(int(mdsteps/60) )
              tmp = (T+(i*T))*kelvin 
              integrator.setTemperature(tmp)
            print(f'Warmed to {tmp} kelvin')

            
            #Add a Barostat if NPT Simulation
            print('Running NPT equilibration...')
            
            if md_params['ensemble'] == "npt":
                system.addForce(MonteCarloBarostat(1.0*atmospheres, int(md_params["temperature"])*kelvin, int(md_params["barostatInterval"])))
                print('Adding Barostat') 
            simulation.context.reinitialize(True)    
            #for i in range(100):
            #    simulation.step(mdsteps/100)
            #    simulation.context.setParameter('k', (float(99.02-(i*0.98))*kilocalories_per_mole/angstroms**2)) #Add weak position restraints maybe?
            #simulation.context.setParameter('k', 0)
            simulation.step(mdsteps) #Actual equilibration run
                
            #Reset timer and step count?
            simulation.saveCheckpoint(output_path+'eq.chk')
            print('Saving simulation checkpoint (equilibrated)')
            
            #Release and recreate
            #FROM HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #del integrator
            #del platform 
            #del platformProperties
            
            #print("Sleeping 3 seconds to allow integrator and platform reinitialization")
            #time.sleep(3) # Sleep for 3 seconds
            
            #platform = Platform.getPlatformByName(md_params['platform']) #Use GPUs to compute
            #if md_params['platform'] == "CUDA":
            #    #platformProperties = {'Precision': } 
            #    platformProperties = {'Precision': str(md_params['precision']), "DeviceIndex": str(deviceindex)}           
            #else:
            #    print("humm.. failed to use the same GPU resource?")
            #    #This is for supporting AMD and CPU in the future
            #    pass    
            
            #Save positions and velocities first
            #simulation.loadCheckpoint(output_path+'eq.chk')
            eq_state   = simulation.context.getState(getVelocities=True, getPositions=True)
            positions  = eq_state.getPositions()
            velocities = eq_state.getVelocities()
            
            #del simulation
            #print("Sleeping 2 seconds to allow simulation object to be deleted")
            #time.sleep(2) # Sleep for 3 seconds
            
            
            #Rebuild the integrator
            #integrator = LangevinMiddleIntegrator(int(md_params["temperature"])*kelvin, 1.0/picosecond, int(md_params["dt"])*femtoseconds) #Create Langevin Integrator - Collision frequency 1ps-1, 2 femtosecond steps at 300 kelvin
            #integrator.setConstraintTolerance(constraintTolerance)
            #print('Resetting simulation timers and step count')
            #simulation = Simulation(prmtop.topology, system, integrator, platform, platformProperties) #Build Simulation object again
            
            simulation.context.setPositions(positions) #Set heated positions
            simulation.context.setVelocities(velocities) #Set heated velocities
            print('Setting heated positions and velocities')
            print('Done equilibrating... ready for production run!')
            
            print("Attaching Data reporters")
            #ATTACH SIMULATION REPORTERS

            #Reformat the path.. see if it works
            output_h5  = os.path.abspath(output_path+output_name+'.h5')
            output_txt = os.path.abspath(output_path+output_textreporter)
            
            #DELETE PREVIOUS H5 TRAJ FILE IF EXISTING
            if(os.path.exists(output_h5)):
                print("h5 file exists.. somehow..Deleting old Trajectory file..")
                os.remove(output_h5)

            #Set reporter frequency (usually a fraction of 1000 for 1000 frames)
            reporterFreq = int(int(md_params["steps"])/int(totalframes))
            print(f"User wants {totalframes} MD frames per file. Setting reporter frequency to {reporterFreq} steps")
                                    
            #Attach ParmedStateReporter - Updates Log File
            simulation.reporters.append(ParmedStateReporter(output_txt, reporterFreq))
            print(f"Attaching ParmedStateReporter trajectory file to {output_txt}")
            #Attach DYMEReporter - Updates Database - 2026 Fix dbhostname in dbreporter
            simulation.reporters.append(DYMEReporter(project_id, mutantID, reporterFreq, "MongoDB", dbhostname))
            print(f"Attaching DYMEReporter hook to DB")
            #Attach HDF5Reporter - Updates TRajectory File
            simulation.reporters.append(HDF5Reporter(str(output_h5), reporterFreq))
            print(f"Attaching MDTraj H5Reporter trajectory file to {output_h5}")
           
            print("Starting simulation")
            
            #for steps in range(1, int(int(md_params["steps"])/10000) ):
            #    simulation.step(10000) #Run for 20ps 
            simulation.currentStep = 0
            simulation.step(int(md_params["steps"])) #Run 

            #UPDATE DATABASE STATUS to "ready_to_scavenge" 
            from DymeDB import DymeDB #spawn again.. after simulation the connection is probably dead, and keepalives don't work
            from datetime import datetime
            db = DymeDB(dbhostname) #New mongodb instance.. from the fork..
            
            q = {'id_project': project_id, 'mutantID': mutantID}
            newvalues = {"$set": { 'status': 'ready_to_scavenge', "status_vars.md_date_end": datetime.now()}}
            db.dbtable_mutants.update_one(q, newvalues)
            
            del simulation
            del integrator
            del platform 
            del platformProperties
            print("Waiting 10 seconds for MD to release the GPU resource")
            time.sleep(10.0) #Wait 10 seconds for objects to release resources. GPUs are set on Exclusive mode.
            print("Simulation released")
       
        except Exception as e: 
            
            print("----------------------!!SIMULATION FAILED!!---------------------------")
            print(str(e))
            print("----------------------------------------------------------------------")
            
            
            from DymeDB import DymeDB
            from datetime import datetime
            db = DymeDB(dbhostname) #New mongodb instance.. from the fork..
            #UPDATE MUTANT RECORD STATUS CODE BACK TO PENDING... WILL BE PICKED UP AGAIN
            q = {'id_project': project_id, 'mutantID': mutantID}
            newvalues = {"$set": { 'status': 'pending', "status_vars.md_date_end": datetime.now()}}    
            db.dbtable_mutants.update_one(q, newvalues)
            print(f"MutantID: {mutantID} has been set to pending again")
                                    
        return    
            
            
            
            
            
            
    def get_gpu_usage(self):
        """
        Returns a dict which contains information about memory usage for each GPU.
    
        In the following output, the GPU with id "0" uses 5774 MB of 16280 MB.
        253 MB are used by other users, which means that we are using 5774 - 253 MB.
    
        {
            "0": {
                "used": 5774,
                "used_by_others": 253,
                "total": 16280
            },
            "1": {
                "used": 5648,
                "used_by_others": 253,
                "total": 16280
            }
        }
    
        """
    
        # Name of current user, e.g. "root"
        current_user = getpass.getuser()
    
        # Find mapping from process ids to user names
        command = ["ps", "axo", "pid,user"]
        output = subprocess.check_output(command).decode("utf-8")
        pid_user = dict(row.strip().split()
            for row in output.strip().split("\n")[1:])
    
        # Find all GPUs and their total memory
        command = ["nvidia-smi", "--query-gpu=index,memory.total", "--format=csv"]
        output = subprocess.check_output(command).decode("utf-8")
        total_memory = dict(row.replace(",", " ").split()[:2]
            for row in output.strip().split("\n")[1:])
    
        # Store GPU usage information for each GPU
        gpu_usage = {gpu_id: {"used": 0, "used_by_others": 0, "total": int(total), "runningone": False}
            for gpu_id, total in total_memory.items()}
    
        # Use nvidia-smi to get GPU memory usage of each process
        command = ["nvidia-smi", "pmon", "-s", "m", "-c", "1"]
        output = subprocess.check_output(command).decode("utf-8")
        for row in output.strip().split("\n"):
            if row.startswith("#"): continue
    
            #gpu_id, pid, type, mb, command = row.split('')
            cols   = list(filter(None, re.split(r'\s{2}', row)))
            print("Row length: "+str(len(cols))) #This changes with nvidia driver versions.. could break soon
            print(cols)
            if len(cols) == 5:
             gpu_id, pid, type, mb, command = cols
            elif len(cols) == 6:
             gpu_id, pid, type, mb, ccm, command = cols
            else:
             gpu_id = cols[0]
             mb     = cols[3]
             pid    = cols[1]

            # Special case to skip weird output when no process is running on GPU
            if pid == "-": continue
            if(mb == " -"):
                mb = 0
            
            #If user wants to launch on a busy GPU (his problem), we fake usage to 0 - PEDRO March 2026
            if  self.reusegpus:
                mb = 0
                

            gpu_usage[gpu_id]["used"] += int(mb)
    
            # If the GPU user is different from us
            try: 
             if pid_user[pid] != current_user:
                gpu_usage[gpu_id]["used_by_others"] += int(mb)
            except:
             gpu_usage[gpu_id]["used_by_others"] += int(mb)
    
        print(gpu_usage)
        return gpu_usage




    def get_free_gpus(self, max_usage_by_others_mb=10):
        """
        Returns the ids of GPUs which are occupied to less than 10 Mb by other users.
        """
        return [gpu_id for gpu_id, usage in self.get_gpu_usage().items() if usage["used"] < max_usage_by_others_mb]


if __name__ == "__main__":
    import argparse

    print("Dynamic Mutagenesis Engine(DyME) v1.0 - MD Worker Node")
    print("Pedro M. Guillem-Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>, Structural Bioinformtics - TU Dresden, Germany")
    print("")

    parser = argparse.ArgumentParser(description="DyME - MD Worker Node  v.1.0")
    parser.add_argument('-d', "--dbhost", type=str, help="Hostname or IP Address of the Main Node instance", required=True)
    parser.add_argument('-u', "--reusegpus", action="store_true",
                        help="Use GPU cards even if they are busy")
    args = vars(parser.parse_args())

    if len(args["dbhost"]) < 2 or args["dbhost"] == "localhost":
        print("-------------------------------------------------------------------------------")
        print("No Hostname or IP address provided... assuming 'localhost' (127.0.0.1)")
        print("-------------------------------------------------------------------------------")
        hostname = "localhost"
    else:
        hostname = args["dbhost"]

    reusegpus = args["reusegpus"]

    node = MD(hostname, reusegpus)
    print("Booting up template Dyme MD node")
    
    node.run()