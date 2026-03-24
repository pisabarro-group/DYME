# -*- coding: utf-8 -*-
"""
DYME - Dynamic Mutagenesis Engine v0.1

File:               DymeTools.py
Description:        Provides Helper Functions

Purpose:            Provides Helper Functions

Provides:          -class DymeTools()

Author:     
Pedro Manuel Guillem Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>
Structural Bioinformatics Laboratory - BIOTEC - Pisabarro Group
Technische Universität Dresden

Feb 2023 -  Added Tleap generators
            Added Mutant generator (cool)

Mar 2023 -  Added mmpbsa generators
            Added NC trajectory file converter
            
Sep 2023 - Added WaterMapper functions (today http://www.github.com/pisabarro-group/WaSiMap.git)

Jan 2024 - Added Contact Scavenger (Forward and Reverse at 10, 20 and 50% thresholds)

"""

import sys
import os
from datetime import date

import multiprocessing as mp
import psutil as ps
from os.path import exists
from subprocess import run, call, Popen, PIPE
from pprint import pprint
from itertools import combinations, product
from io import StringIO
import pandas as pd
import h5py as h5
import operator as op
import mdtraj as md
import numpy as np

from modeller import *
from modeller.automodel import *

import parmed as pm



"""
Contains routines for extracting contacts wvd/hbonds with cpptraj

Constructor:
        - Contacts(projectID, mutantID, path)

Pedro: Jan 11 2024
"""     
class Contacts:
    
    projectID = 0
    mutantID  = 0
    path_trajectory = 0
    
    #PENDING TO IMPORT NEWER VERSION OF DYMEWATER - RETURNS ARRAY OF DICTIONARIES
    #Watch out.. distance threshold comes in nanometers, not angstroms
    def __init__(self, projectID, mutantID, proj):
        #Assign Variables
        self.projectID          = projectID
        self.mutantID           = mutantID
        self.project            = proj
        self.cpptrajf           = {}
        self.cpptrajr           = {}
                
    #Computes all trajectory contacts using cpptraj                
    def computeContacts(self):
        
        import pytraj as pt
        import re
        import gc

        map        = self.project['residuemap']
        objs       = self.project['objects']
        path       = self.project['project_folder']
        mutantdir  = f"{path}/mutants/{self.mutantID}"
        prmtop     = f"{mutantdir}/inputs/receptor_ligand_wat.prmtop"
        trajectory_h5 = f"{mutantdir}/outputs/output_md.h5"
        trajectory_nc = f"{mutantdir}/outputs/output_md.nc"

        #DNA Bases to probe whether we should extract 2 or 3 letter codes
        dna_bases = ["DA","DG","DC","DA"]
        
        print(f"Loading trajectory for project {self.projectID} mutant {self.mutantID}")
        
        #Get which object is which
        for prop in objs:
            if prop['mutable'] == True:
                mutchain_target = prop["chains"][0]["key"]
        
        #SPLIT MOLECULAR OBJECTS IN TWO (receptor / ligand) ARRAYS
        dict_receptor = {}
        dict_ligand   = {}
        
        ligmask = []
        recmask = []
        
        #Iterate project map
        for obj in map:
            for mut in map[obj]:
                if mut is not None:
                    position_pdb = mut["resno_PDB"]
                    position_ngl = mut["resno_NGL"]
                    residue      = mut["name"]
                        
                    pdb_map = f"{residue}{position_pdb}"
                    ngl_map = f"{residue}{position_ngl}"
                                        
                    if mut["chain"] == mutchain_target:
                        #Ligand
                        ligmask.append(position_ngl)
                        dict_ligand[str(ngl_map)] = {
                            "pdb": pdb_map,
                            "ngl": ngl_map,
                            "ngl_pos": position_ngl,
                            "hbonds": []
                        } 

                    else:
                        #Receptor
                        recmask.append(position_ngl)
                        dict_receptor[str(ngl_map)] = {
                            "pdb": pdb_map,
                            "ngl": ngl_map,
                            "ngl_pos": position_ngl,
                            "hbonds": []
                        }
        #Get acceptor/donor amber masks - from min and max ngl positions of receptor and ligand
        acceptormask = f":{min(recmask)}-{max(recmask)}" #This is used with pytraj afterwards - RECEPTOR
        donormask    = f":{min(ligmask)}-{max(ligmask)}" #This is used with pytraj afterwards - LIGAND
        
        
        #Use pytraj to do the rest
        #1. convert mdtraj h5 to pytraj
        traj = md.load(trajectory_h5)
        if not os.path.isfile(trajectory_nc):
            print("Creating NC trajectory")
            traj.save_netcdf(trajectory_nc)
            print("NC Created")
        else:
            print("NC trajectory already esists.. skipping")

        

        #Add any aditional positions involving a mutation to comparison dicts- FEB 8 2024
        #traj = traj.remove_solvent() #No waters please - This shitty library removes 2 sincs and treats them as solvent.. fucks shit up
        residues = list(traj.topology.residues) #Get residue list

        for pos in ligmask:
            ind = str(residues[pos-1])
            if ind not in dict_ligand:
                print(f"Adding {ind} with pos {pos-1}")
                dict_ligand[ind] = {
                                "ngl": ind,
                                "ngl_pos": pos,
                                "hbonds": []
                }
       
        print("FInished Ligmask check")
        #Complement receptor_dict with mutated positions
        for pos in recmask:
            ind = str(residues[pos-1])
            if ind not in dict_receptor:
                print(f"Adding {ind}")
                dict_receptor[ind] = {
                            "ngl": ind,
                            "ngl_pos": pos,
                            "hbonds": []
                }
            
        #Load NC trajectory with iterload (extremely faster than converting xyz from mdtraj)
        traj = None
        gc.collect()
        #print("Loading Iterload Pytraj Trajectory")
        traj = pt.iterload(trajectory_nc, prmtop)
        
        #Compute all VDW contacts (insanely fast...wothout waters offcourse)
        #print(f"AMBER MASKS acceptormask {acceptormask} donormask {donormask}")
        vdw  = pt.search_hbonds(traj, angle=135, distance=3.5, options=f"acceptormask {acceptormask} donormask {donormask}")
        vdw2 = pt.search_hbonds(traj, angle=135, distance=3.5, options=f"acceptormask {donormask} donormask {acceptormask}")
        #Get dictionaries of vdw a to b --- and b to a
        a2b = vdw.to_dict()
        b2a = vdw2.to_dict()
        
        #ADDED FUNCTION TO CALCULATE DIFFERENT THRESHOLDS - PEDRO FEB 12
        def classifyContacts(threshold):

            vdw_lig = {}
            vdw_rec = {}
            
            #Organize a2b - From Receptor to Ligand
            for bond in a2b.items():
                if len(bond) > 0:
                    if sum(bond[1]) > (traj.n_frames/threshold): #10% of trajectory is the minimum relevant contact
                        if str(bond[0]) != "total_solute_hbonds":
                            #print(str(bond[0]))
                            A,B = str(bond[0]).split("-", 1)
                            resA, atomA = A.split("_")
                            resB, atomB = B.split("_")

                            if (resA in dict_receptor) and (resB in dict_ligand):
                                if(resB not in vdw_lig):
                                    vdw_lig[resB] = [{resA: atomB+"_"+atomA}]
                                else: 
                                    vdw_lig[resB].append({resA: atomB+"_"+atomA})
                            
                            if (resA in dict_ligand) and (resB in dict_receptor):
                                if(resA not in vdw_lig):
                                    vdw_lig[resA] = [{resB: atomA+"_"+atomB}]
                                else: 
                                    vdw_lig[resA].append({resB: atomA+"_"+atomB})
                                        
            #Organize b2a - From Ligand to Receptor
            for bond in b2a.items():
                if len(bond) > 0:
                    if sum(bond[1]) > (traj.n_frames/threshold): #10% of trajectory is the minimum relevant contact
                        if str(bond[0]) != "total_solute_hbonds":
                            #print(str(bond[0]))
                            A,B = str(bond[0]).split("-", 1)
                            resA, atomA = A.split("_")
                            resB, atomB = B.split("_")
                            if (resA in dict_receptor) and (resB in dict_ligand):
                                if(resB not in vdw_lig):
                                    vdw_lig[resB] = [{resA: atomB+"_"+atomA}]
                                else: 
                                    vdw_lig[resB].append({resA: atomB+"_"+atomA})
                            
                            if (resA in dict_ligand) and (resB in dict_receptor):
                                if(resA not in vdw_lig):
                                    vdw_lig[resA] = [{resB: atomA+"_"+atomB}]
                                else: 
                                    vdw_lig[resA].append({resB: atomA+"_"+atomB})

            #################### BACKWARDS COMPUTATION #######################
            #Organize a2b - From Receptor to Ligand
            for bond in a2b.items():
                if len(bond) > 0:
                    if sum(bond[1]) > (traj.n_frames/threshold): #10% of trajectory is the minimum relevant contact
                        if str(bond[0]) != "total_solute_hbonds":
                            #print(str(bond[0]))
                            A,B = str(bond[0]).split("-", 1)
                            resA, atomA = A.split("_")
                            resB, atomB = B.split("_")
                            
                            if (resA in dict_ligand) and (resB in dict_receptor):
                                if(resB not in vdw_rec):
                                    vdw_rec[resB] = [{resA: atomB+"_"+atomA}]
                                else: 
                                    vdw_rec[resB].append({resA: atomB+"_"+atomA})
                                    
                            if (resA in dict_receptor) and (resB in dict_ligand):
                                if(resA not in vdw_rec):
                                    vdw_rec[resA] = [{resB: atomA+"_"+atomB}]
                                else: 
                                    vdw_rec[resA].append({resB: atomA+"_"+atomB})
                            
                                        
            #Organize b2a - From Ligand to Receptor
            for bond in b2a.items():
                if len(bond) > 0:
                    if sum(bond[1]) > (traj.n_frames/threshold): #10% of trajectory is the minimum relevant contact
                        if str(bond[0]) != "total_solute_hbonds":
                            #print(str(bond[0]))
                            A,B = str(bond[0]).split("-", 1)
                            resA, atomA = A.split("_")
                            resB, atomB = B.split("_")
                            
                            if (resA in dict_ligand) and (resB in dict_receptor):
                                if(resB not in vdw_rec):
                                    vdw_rec[resB] = [{resA: atomB+"_"+atomA}]
                                else: 
                                    vdw_rec[resB].append({resA: atomB+"_"+atomA})
                                    
                            if (resA in dict_receptor) and (resB in dict_ligand):
                                if(resA not in vdw_rec):
                                    vdw_rec[resA] = [{resB: atomA+"_"+atomB}]
                                else: 
                                    vdw_rec[resA].append({resB: atomA+"_"+atomB})
                    
            #CLASSIFICATION 
            #os.remove(trajectory_nc)
            #print("Removing NC trajectory from Disk")
            print("Contact information computed correctly")
            
            self.cpptrajf[threshold] = vdw_lig
            self.cpptrajr[threshold] = vdw_rec
        
        classifyContacts(10) #10%
        classifyContacts(5)  #20%
        classifyContacts(2)  #50%

        #self.cpptrajf = vdw_lig[]
        #self.cpptrajr = vdw_rec[]


    #Return Forward Contacts 
    def getForwardContacts(self, threshold):
        return self.cpptrajf[threshold]


    #Return Reverse contacts
    def getReverseContacts(self, threshold):
        return self.cpptrajr[threshold]







"""
Contains routines for mapping of wetspots from a given trajectory

Constructor:
        - WaterMapper(projectID, mutantID, distance_threshold=3.5, persistence_threshold=10)

"""     
class WaterMapper:
    
    projectID = 0
    mutantID  = 0
    around_nanometers = 0
    relevance = 0 
    n_frames = 0
    
    
    #Watch out.. distance threshold comes in nanometers, not angstroms
    #persistence_threshold comes in number of frames for a water to be considered "relevant". This is usually 1% of frames
    def __init__(self, projectID, mutantID, path, distance_threshold=0.35, persistence_threshold=0.006):
        #Assign Variables
        self.projectID          = projectID
        self.mutantID           = mutantID
        self.around_nanometers  = distance_threshold #In angstroms
        self.relevance          = persistence_threshold#in percentage
        self.path               = path #Full path to H5 trajectory
        
        #Load trajectory into main memory
        self.traj = ""
        
    def loadTrajectory(self):
        
        print(f"Loading trajectory in {self.path} for project {self.projectID} mutant {self.mutantID}")
        self.traj = md.load(self.path)
        print(f"Imaging trajectory to single periodic box")
        self.traj.image_molecules(inplace=True)
        self.nframes  = self.traj.n_frames
   
   
    def findWetSpots(self, map):
            from multiprocessing import Process
            from multiprocessing import Manager 
            import numpy as np
                  
            print(f"Processing WaterMapper for MutantID {self.mutantID}")
            traj = md.load(self.path)
            
            # 1. Image molecules (fix broken molecules due to PBC)
            print("WaterMapper:  Performing trajectory Image/center/superpose - This could take a long time")
            print("Imaging...")
            traj.image_molecules(inplace=True)
            
            # 2. Center coordinates (move system to origin, solvent included)
            print("Centering...")
            traj.center_coordinates()
            
            # 3. Align entire system to the first frame (solvent + protein)
            print("Superposing around frame 0...")
            traj.superpose(traj, frame=0)
            print("WaterMapper:  OK. Molecules centered")

            around_nanometers = self.around_nanometers #cuttof distance from water to heavy atom
            nframes           = traj.n_frames #number of frames in the trajectory
            relevant          = nframes*self.relevance #minimum residence frames to be considered a relevant water
            #relevant          = 100 #This is true for most simulations (5% for 1000 - 0.5% for 10000 frames)
            involved_ids      = [] #Ids of atoms that we want to analyze (interfacial atoms)
            
            #PEDRO 2024 - Change the way we obtain interfacial atoms
            residuemap = map['residuemap']
            masks = {}
            for chain, residues in residuemap.items():
                # Filter out None values
                valid_residues = [res for res in residues if res is not None]#Select records that are not none
                
                if valid_residues:
                # Extract the first and last resno_NGL values
                    first_resno = valid_residues[0].get("resno_NGL")
                    last_resno  = valid_residues[-1].get("resno_NGL")
                    #PEDRO - 2025 I changed the mdtraj query selector to not limit selection to 'protein' residues, as DNA may be the receptor.. mdtraj 
                    #selector language can't match DNA bases... so we trust the residuemap alone.. which comes from the project wizard. 
                    #masks[chain] = traj.topology.select(f"resid {first_resno} to {last_resno} and protein and not element H and not element C")
                    masks[chain] = traj.topology.select(f"resid {first_resno} to {last_resno} and not element H and not element C")
            
            #USually we will have 2 chains in the complex (ligand and receptor). We assume this for now.
            #It could happen that the input PDB has more than 2 chains.. in this split will fail
            chain_1, chain_2 = masks.values()

            # Create all pair combinations between chain A and B atoms
            print(f"Finding interfacial Atoms")
            atom_pairs = np.array([[i, j] for i in chain_1 for j in chain_2])
            print(f'chain 1 {chain_1} and chain 2 {chain_2}')
            print(f"Computing distances from residues between ligand and receptor molecules with MDTraj")
            distances  = md.compute_distances(traj, atom_pairs)
            cutoff     = 0.5 # reasonable distance from A to B.. to be considered interfacial distance
            close_contact_mask = np.any(distances < cutoff, axis=0) #get the distance mask
            interfacial_pairs  = atom_pairs[close_contact_mask]
            print(f"Pairs computed, flattening..")
            # Get unique interfacial atoms
            interfacial_atoms = np.unique(interfacial_pairs.flatten())
            involved_ids = interfacial_atoms.tolist()         
            print(f"{len(involved_ids)} atoms queued for analysis")
            
                                
            #print(f"Added all heavy atoms that form intermolecular Hbonds")

            #Calculate euclidean distance from every molecule of water to AtoMID, in every frame.
            #I do this in a function, so we can enqueue in a process pool of all involved atom ids at the same time - takes around 20 seconds vs 3 minutes one by one
            def processAtom(id, anchordict):
                #for id in involved_ids:
                print(f"Processing AtomID {id}")
                wadict = {}
                for water in waters:
                    framebyframe = np.sqrt(np.sum((traj.xyz[:, water, :] - traj.xyz[:, id, :])**2, axis=1))
                    framenum = 0
                    selectedframes = [] #Stores coordinates of frames
                    for euclidean in framebyframe: #Iterate euclidean distance of waters to IDS in the matrix
                        if euclidean <= around_nanometers:
                                if wadict.get(water) == None:
                                    wadict[water] = []
                                selectedframes.append(framenum)
                        framenum=framenum+1
                    wadict[water] = selectedframes
                    if wadict.get(water) != None:
                        if len(wadict[water]) < 20: #Ditch meaningless water.. we assume if the water occupies a site less than 50 frames, is not representative
                            wadict.pop(water)
                anchordict[id] = wadict
                #print(anchordict)
                print(f"##############FINISHED ATOM {id}###############")
            
            '''
            #Launch Processes in Parallel
            manager = Manager() #Create a manager processing pool
            involved_ids = list(set(involved_ids)) #Remove duplicates from atom list
            print(f"Involved AtomIDs {involved_ids}")
            #GET ids of Oxygens in water atoms
            waters = traj.topology.select("(water) and (symbol == 'O')")
            waterdict = {}
            anchordict = manager.dict()
            jobs    = [] #Process pool
            
            #Create a process per AtomID
            for id in involved_ids:
                anchordict[id] = {}
                p = Process(target=processAtom, args=(id, anchordict))
                jobs.append(p)
                p.start()

            #Launch parallel jobs    
            for proc in jobs:
                proc.join()
                        
            '''
            # involved_ids already defined above
            involved_ids = list(set(involved_ids))
            print(f"Involved AtomIDs {involved_ids}")

            # waters already depends on traj, so compute once
            waters = traj.topology.select("(water) and (symbol == 'O')")

            # use a plain dict; we are already inside a process, so threads can share it
            anchordict = {}

            # fan-out with threads (NOT processes) to avoid nested-fork + Manager proxy issues
            from concurrent.futures import ThreadPoolExecutor
            import os

            max_workers = min(16, max(8, (os.cpu_count())))  # modest parallelism
            with ThreadPoolExecutor(max_workers=max_workers) as ex:
                # pre-seed keys if you want to keep your behavior
                for _id in involved_ids:
                    anchordict[_id] = {}
                # launch the work
                list(ex.map(lambda _id: processAtom(_id, anchordict), involved_ids))

            #print("this is what came out")
            #print(anchordict)
            #Define a list of important water ids
            importantwaters = {} #Stores all important waterIDs, frame arrays near, and residence percentage
            anchorcontacts  = {} #Stores anchorpoint and for each the waterids that crossed it
            watersites = {} #Stores the average coordinates of the watersites, and the waters involved
            watersiteid = 1
            for anchor, waters in anchordict.items():
                anchor = str(anchor)
                owat = {k: v for k, v in sorted(waters.items(), key=lambda item: item[1], reverse=True)}
                print(f"{len(waters)} waters crossed near anchor-atom {anchor}")
                aguas = []
                for atom, frames in owat.items(): #atom is the water atom ID, frames is an array of frames where water was near anchor
                    if len(frames) >= relevant:
                        print(f"Appending {atom} to list of importants ({len(frames)} frames)")
                        
                        if importantwaters.get(str(atom)) == None:
                            importantwaters[str(atom)] = {}
                        
                        importantwaters[str(atom)]['residue'] = str(traj.topology.atom(atom)) #The water residue (not atom id)
                        importantwaters[str(atom)]['frames']  = frames #array of frame indexes where water was near
                        #PEDRO 2025 - ADD OCCUPANCY/RESIDENCE 
                        atom_coords = traj.xyz[frames, atom, :]  # Shape: (selected_frames, water_atomid) # Gets an np array of 3d coords of water at selected frames
                        # Compute the average position (x, y, z)
                        average_position = np.mean(atom_coords, axis=0)#get the mean 3D position of this water (defines a water site)
                        average_position *= 10 #convert to Angstroms (units are in nanometers)
                        importantwaters[str(atom)]['residence_percentage']  = round((len(frames)/nframes)*100) #Get the residence time of this water
                        importantwaters[str(atom)]['wetspot']  = average_position.tolist() #Numpy array
                        #x_avg, y_avg, z_avg = average_position 
                        #print(f"X  : {x_avg}, Y: {y_avg}, Z: {z_avg}")
                        if anchorcontacts.get(anchor) == None:
                            anchorcontacts[anchor] = {}
                        
                        anchorcontacts[anchor]['residue'] = str(traj.topology.atom(int(anchor))) #anchorpoint residue in RESPOS-ATOM format
                        aguas.append(int(atom)) 
                if len(aguas) > 0:
                    
                    #BUILD WATERSITES
                    coords = []
                    for agua in aguas:
                           coords.append(importantwaters[str(agua)]['wetspot'])
                    centroid = np.mean(np.array(coords), axis=0)
                    centroid = centroid.tolist()
                    #BUILD ANCHOR WATER ARRAY
                    anchorcontacts[anchor]['waters'] = aguas #water atom ids that crossed this anchor
                    anchorcontacts[anchor]['watersite_centroid'] = centroid
            
            print(f"Updating Processed_Data table with water info for mutant {self.mutantID}")
            res  = {'anchor_contacts' : anchorcontacts, 'important_waters': importantwaters}
            
            print("###########################")
            return res
        
        
        
        
        
        


"""
Controls the creation of MMPBSA.py input files and directories

Constructor:
        - mmgbsaGen(mutantID, AmberSelector, inputPath, startFrame, endFrame, interval)

"""     
class MMGBSA:
    
    template_perresidue = """&general
   startframe={{startFrame}},
   endframe={{endFrame}},
   interval={{interval}},
   verbose=2,
   keep_files=0,
/
&gb
   igb={{igbValue}},
/
&decomp
   idecomp=2, {{printSel}}
   dec_verbose=3,
"""  

    template_pairwise = """&general
   startframe={{startFrame}},
   endframe={{endFrame}},
   interval={{interval}},
   verbose=2,
   keep_files=0,
/
&gb
   igb={{igbValue}},
/
&decomp
   idecomp=4, {{printSel}}
/
"""

    template_perresidue_pb = """&general
   startframe={{startFrame}},
   endframe={{endFrame}},
   interval={{interval}},
   verbose=2,
   keep_files=0,
/
&pb
   istrng=0.100, inp={{inpValue}}
/
&decomp
   idecomp=2, {{printSel}}
   dec_verbose=3,
"""  

    template_pairwise_pb = """&general
   startframe={{startFrame}},
   endframe={{endFrame}},
   interval={{interval}},
   verbose=2,
   keep_files=0,
/
&pb
   istrng=0.100, inp={{inpValue}}
/
&decomp
   idecomp=4, {{printSel}}
/
"""

    name_pairwise   = "pairwise.in"
    name_perresidue = "perresidue.in"
    launcher_pairwise   = ""
    launcher_perresidue = "" 
    

    #SET MMPBSA VARS
    #outPath is mutant toplevel directory
    def __init__(self, mutantID=0, receptorSel="", ligandSel="", outPath="", startFrame=100, endFrame=10000, interval=30, igb=2, inp=1, compute_mode=""): 
        
         self.path       = outPath
         self.startFrame = startFrame
         self.endFrame   = endFrame
         self.interval   = interval
         self.mutantID   = mutantID
         self.igbVal     = igb
         self.inpVal     = inp
         self.compute_mode = compute_mode
         
         #Track only certain residues if desired
         if receptorSel  != "" and ligandSel != "":
             self.printSel = f'print_res="{ligandSel}; {receptorSel}"'
         else:
             self.printSel = ""
        
         print(f'Created MMGBSA instance for mutant {self.mutantID}')





    #Create mmgbsa flag files from templates
    def makeInputs(self):
        
        print(f'Generating MMPBSA.py.MPI input flags for mutant {self.mutantID}')
        
        REPLACEMENTS = [
            ("{{startFrame}}", self.startFrame),
            ("{{endFrame}}", self.endFrame),
            ("{{interval}}", self.interval),
            ("{{printSel}}", self.printSel),
            ("{{igbValue}}", self.igbVal), #Add igb 2 or 8 option, for protein or protein-dna systems
            ("{{inpValue}}", self.inpVal)
        ]
        
        #Replace in pairresidue
        self.perresidue = self.template_perresidue
        if self.compute_mode == "energy_pbsa":
            self.perresidue = self.template_perresidue_pb
        
        for old, new in REPLACEMENTS:         
            self.perresidue = self.perresidue.replace(old, str(new))
            
        #Replace in pairwise
        self.pairwise = self.template_pairwise
        if self.compute_mode == "energy_pbsa":
            self.pairwise = self.template_pairwise_pb
        for old, new in REPLACEMENTS:         
            self.pairwise = self.pairwise.replace(old, str(new))
        
        print(f'Created Pariwise/Perresidue flag files for {self.compute_mode} mode!')






    #Wite 
    def writeInputs(self):
        #create in wildtype directory
        targetdir = f'{self.path}/inputs/mmgbsa/'

        if not os.path.exists(targetdir):
          os.makedirs(targetdir)
        
        with open(targetdir+self.name_pairwise, "w+") as f:
           f.write(self.pairwise)
        
        with open(targetdir+self.name_perresidue, "w+") as f:
           f.write(self.perresidue)
           
        print(f'Wrote files to {targetdir}')
    
    def setRamDisk(self, pin, pout):
        self.ramdisk_in  = pin
        self.ramdisk_out = pout
                        
    
    #Create a NC trajectory from HDF5    
    def genNCtrajectory(self, path):
        origdir = f'{path}/outputs'
        targetdir = self.ramdisk_out
        if os.path.exists(f'{targetdir}/output_md.nc'):
            os.remove(f'{targetdir}/output_md.nc')
        
        #print('Creating NC format of the original HDF5 trajectory in Ramdrive!')
        #run([cmd], cwd=targetdir, stdin=PIPE, shell=True, executable='/bin/bash')     
        traj  = md.load_hdf5(f'{origdir}/output_md.h5')
        traj.save_netcdf(f'{targetdir}/output_md.nc')
        print('NC Trajectory created!')
        del traj
        print('Closing H5 handler!')
            
    
    
    #Delete NC trajectory
    def delNCtrajectory(self, path):
        #targetdir = f'{path}/outputs'
        targetdir = self.ramdisk_out
        print('Removing .NC trajectory from database')
        if os.path.exists(f'{targetdir}/output_md.nc'):
            os.remove(f'{targetdir}/output_md.nc')
        print("NC trajectory Dropped ")
        print("-------------------------------------------")
    
    
    
    
        
    
    #Build launch execs for both MMGBSA       routines  
    def launchCodes(self, cpus=8):   
        res = {}
        ram_in  = self.ramdisk_in
        ram_out = self.ramdisk_out
        
        #Pairwise flags        
        infile_pa   = f'-i  {self.path}/inputs/mmgbsa/{self.name_pairwise}'
        outfile1_pa = f'-o  {self.path}/outputs/output_pairwise.dat'
        outfile2_pa = f'-do {self.path}/outputs/output_pairwise_decomp.dat'
        
        #Perresidue flags        
        infile_pr   = f'-i  {self.path}/inputs/mmgbsa/{self.name_perresidue}'
        outfile1_pr = f'-o  {self.path}/outputs/output_perresidue.dat'
        outfile2_pr = f'-do {self.path}/outputs/output_perresidue_decomp.dat'        
        
        #Common to all
        wet      = f'-sp {self.path}/inputs/receptor_ligand_wat.prmtop'
        dry      = f'-cp {self.path}/inputs/receptor_ligand.prmtop'
        rec      = f'-rp {self.path}/inputs/receptor.prmtop'     
        lig      = f'-lp {self.path}/inputs/ligand.prmtop'
        traj     = f'-y {ram_out}/output_md.nc'
        
        #Build command launchers - See MMBPSA.py.MPI documentation
        res["pairwise"]   = f'mpirun -np {cpus} MMPBSA.py.MPI -O {infile_pa} {outfile1_pa} {outfile2_pa} {wet} {dry} {rec} {lig} {traj}'
        res["perresidue"] = f'mpirun -np {cpus} MMPBSA.py.MPI -O {infile_pr} {outfile1_pr} {outfile2_pr} {wet} {dry} {rec} {lig} {traj}'
        return res





    #Takes GBSA pairwise .dat, parses it - and it stores it in the DB
    def parse_deltaG(self):
        
        outfile = f'{self.path}/outputs/output_pairwise.dat' #Technically either file should work for this
        
        #Make sure the file is there
        if not os.path.exists(outfile):
            print("OOPS! - GBSA main file not found?? wtf")
            return {}
        
        print(f"Scavenging Total DeltaG values for {self.mutantID}")
        cmd = f'tail -n21 {outfile} | grep "DELTA TOTAL"'
        p = Popen([cmd], shell=True, stderr=PIPE, stdout=PIPE) #Read the last 20 files (last table)
        res, err = p.communicate() #Get the juice
        deltatuple =  str(res).split()        
        deltas = {"deltag_total": deltatuple[2], "deltag_std": deltatuple[3]}
        
        #Returns dictionary of Delta Total and Delta Std on the .dat file for this mutant
        return deltas        
    
    
    

    #Parses GBSA_decomp_pairwise and it stores it in the DB
    def parse_Pairwise(self, anchorpoints=[]):
        #COLUMN NAMES OF PAIRWISE FILE
        head = ['RES1','RES2', 'INT_AVG', 'INT_STD', 'INT_ERR', 'VDW_AVG', 'VDW_STD', 'VDW_ERR', 'ELEC_AVG', 'ELEC_STD', 'ELEC_ERR', 'POL_AVG', 'POL_STD', 'POL_ERR', 'NPOL_AVG', 'NPOL_STD', 'NPOL_ERR','TOT_AVG','TOT_STD','TOT_ERR']
        
        #Check that the file exists before trying to read it
        outfile = f'{self.path}/outputs/output_pairwise_decomp.dat'
        if not os.path.exists(outfile):
            print("OOPS! - GBSA _pairwise_decomp file not found?? wtf")
            return {}
        print(f"Scavenging Pairwise energy values for {self.mutantID}")
        #Read CSV into a Dataframe.. manipulate
        deltas = pd.read_csv(outfile, sep=",",skiprows=9) #Start reading from row 9 (hopefully it never changes in MMPBSA)
        deltas = deltas.set_axis(head, axis=1) #Set/rename axis columns
        deltas.index +=1 #Rebuild indexes from 1, not 0
        deltas = deltas.dropna(axis=0, how='any')
        #PEDRO MARCH 28 - Had to get rid of the digit regexp, this reorders the dataframe in an undesired way.
        #Remove text from columns 1 and 2 - we only care about the residue index, not the residue
        deltas['RES1'] = deltas['RES1'].str.replace(r'^(.+)\s', '', regex=True)
        deltas['RES2'] = deltas['RES2'].str.replace(r'^(.+)\s', '', regex=True)
        
        #Filter only those records containing anchorpoint data in column RES1
        deltas = deltas[deltas['RES1'].isin(anchorpoints)]
        
        deltas['RES1'] = deltas['RES1'].astype(int)
        deltas['RES2'] = deltas['RES2'].astype(int)
        
        deltas.index = deltas.index.map(str) #Convert int indexes to string indexes, mongoDB doesnt like them
        return deltas.to_dict() #Return the dictionary... to be built by caller function in Scavenger
    
    
    
    
    #Parses GBSA_decomp_perresidue and it stores it in the DB
    def parse_Perresidue(self):
        #COLUMN NAMES OF PERRESIDUE FILE        
        head = ['RES', 'LOC', 'INT_AVG', 'INT_STD', 'INT_ERR', 'VDW_AVG', 'VDW_STD', 'VDW_ERR', 'ELEC_AVG', 'ELEC_STD', 'ELEC_ERR', 'POL_AVG', 'POL_STD', 'POL_ERR', 'NPOL_AVG', 'NPOL_STD', 'NPOL_ERR','TOT_AVG','TOT_STD','TOT_ERR']

        outfile = f'{self.path}/outputs/output_perresidue_decomp.dat'
        if not os.path.exists(outfile):
            print("OOPS! - GBSA _perresidue_decomp file not found?? wtf")
            return {}
        
        print(f"Scavenging Per-residue energy values for {self.mutantID}")
        exec_string = f"cat {outfile} | sed -n '/DELTAS:/,/Sidechain/p'" #Get only the DELTAS table from file
        
        p = Popen([exec_string], shell=True, stderr=PIPE, stdout=PIPE) #Read the file from OS (Linux Only)
        res = p.communicate()[0] #Get command output (chunk of file we need.. with some trailing garbage)
        
        res = list(map(lambda x: x.split(','),res.decode('utf-8').split("\r\n"))) #Build a list from linebreaks
        
        deltas        = pd.DataFrame(res[4:]) #Get Dataframe from row 4 and onwards
        deltas        = deltas.set_axis(head, axis=1) #rename columns with something comprenhensive
        deltas.index +=1 #Reindex dataframe from 1, not 0
        deltas.index  = deltas.index.map(str) #Convert int indexes to string indexes, mongoDB doesn;t like them
        deltas        = deltas.dropna(axis=0, how='any') #Delete lines where any column is blank or zero (garbage)
        deltas['RES'] = deltas['RES'].str.replace(r'^(.+)\s','', regex=True).astype(int) #Get the RES column with the ID only

        #Return a Dataframe with Deltas Table of the Pairresidue file (all columns)
        #index starts at 1 for residue 1.. coincides with residue position
        return deltas.to_dict() #Return the dictionary... to be built by caller function in Scavenger


    #Get best frame from a mutant
    def parse_BestFrame(self):
        infile   = f'{self.path}/outputs/output_md.h5'
        outfile  = f'{self.path}/outputs/output_bestpdb.pdb'
        outfile2 = f'{self.path}/outputs/output_bestpdb_wat.pdb'
        
        #Get frame with best potentialEnergy from HDF5 array
        print(f'Finding Best Frame of Mutant {self.mutantID}')
        f         = h5.File(infile, "r")
        best      = min(enumerate(list(f["potentialEnergy"])), key=op.itemgetter(1))
        bestframe = best[0]
        value     = float(best[1])
        f.close()
        del f #Delete
        
        print(f'Best frame is {bestframe}')
        #Make PDBs (of best frame)
        print(f'Writing Wet and Dry PDBs of best frame of Mutant {self.mutantID}')
        traj = None
        repeat = True
        tries = 0
        while repeat and tries < 5:
            try: 
                traj  = md.load_hdf5(infile)
                print(f'Opened trajectory at {infile}')
                print(f'Imaging molecules')
                traj.xyz
                traj.image_molecules(inplace=True)
                traj.xyz
                print(f'Centering coordinates')
                traj.center_coordinates()
                print(f'Superposing trajectory to first frame')
                traj.superpose(traj, frame=0)   
                print(f'Extracting PDB at best Frame')
                wet = traj[bestframe]
                print(f'Step 1')
                arr = wet.top.select("not water")
                print(f'Step 2')
                dry = wet.atom_slice(arr)
                #Write PDBs
                print(f'Step 3')
                dry.save_pdb(outfile)
                print(f'Step 4')
                wet.save_pdb(outfile2)
                print(f'Step 5')
                tries = 10
                repeat = False
            except:
                tries = tries+1
                print(f"Trying {tries} times.. repeating")
                del traj
                pass
            
        del traj
        
        return [bestframe, value]
    
    def parse_RMSD(self):
        infile   = f'{self.path}/outputs/output_md.h5'
        traj     = md.load_hdf5(infile)
        rmsd     = md.rmsd(traj,traj, 0) #RMSD With respect to first frame of the same trajectory
        del traj
        return rmsd.tolist()      
    
    
    def parse_Hbonds(self):
        infile   = f'{self.path}/outputs/output_md.h5'
        traj     = md.load_hdf5(infile)
        hbonds   = md.baker_hubbard(t, periodic=False, sidechain_only=True, freq=0.1, exclude_water=False)
        label    = lambda hbond : '%s -- %s' % (t.topology.atom(hbond[0]), t.topology.atom(hbond[2]))
        del traj
        return hbonds






"""
Controls the creation of TLEAP input files for a given mutant

Constructor:
        - tleapGen(tleapParams)

"""     
class tleapGen:
    
    template = """#Dyme_Generated Tleap File
#Project ID       {{projectID}}
#Project Name     {{projectName}}
#Date created     {{createDate}}
#Target directory {{targetDirectory}}

{{sources}}
{{addAtomTypes}} 
{{offFiles}}
{{amberPreps}}
{{amberParams}}

#Bondradii default
{{bondRadii}}

#Load Input Complex Structure
a = loadpdb {{targetDirectory}}{{inputPdbFile}}

{{bondInfo}}

savepdb a {{targetDirectory}}/receptor_ligand.pdb

#Create Parameters and Topology
saveamberparm a {{targetDirectory}}/receptor_ligand.prmtop {{targetDirectory}}/receptor_ligand.inpcrd

#Solvate Model
{{boxShape}} a {{waterBoxModel}} {{boxSize}}
addIonsRand a {{negativeIon}} {{molarStr}} 5
addIonsRand a {{positiveIon}} {{molarStr}} 5

savepdb a {{targetDirectory}}/receptor_ligand_wat.pdb
saveamberparm a {{targetDirectory}}/receptor_ligand_wat.prmtop {{targetDirectory}}/receptor_ligand_wat.inpcrd
quit
"""
        
    
    #SET INITIAL LEAP VARIABLES -
    def __init__(self, leapParams, path, projectID, mutantID=0):  
        
        if mutantID == 0:
            #create in wildtype directory
            targetdir = f'{path}/inputs/'
        else:
            #create in mutant directory
            targetdir = f'{path}/mutants/{mutantID}/inputs/'  #Dir holding all input files for MD
            outputdir = f'{path}/mutants/{mutantID}/outputs/' #Dir holding all output files of MD & Analysis

            if not os.path.exists(f'{path}/mutants/{mutantID}'):
                os.makedirs(f'{path}/mutants/{mutantID}')
        
            if not os.path.exists(targetdir):
                os.makedirs(targetdir)
            
            if not os.path.exists(outputdir):
                os.makedirs(outputdir)    
        
        
        self.projectID       = projectID
        self.projectName     = leapParams["projectName"]
        self.createDate      = leapParams["createDate"]
        self.targetDirectory = targetdir
        self.addAtomTypes    = leapParams["addAtomTypes"]
        self.bondInfo        = leapParams["bondInfo"]
        self.leapSources     = leapParams["leap_sources"]
        self.leapFiles       = leapParams["leap_files"] 
        self.inputPdbFile    = leapParams["inputPdbFile"]
        self.leapSourcesDirectory = leapParams["leapSourcesDirectory"]
        self.boxShape        = leapParams["boxShape"]   
        self.waterBoxDistance= leapParams["boxSize"]
        self.waterBoxModel   = leapParams["watModel"]
        self.boxSize         = leapParams["boxSize"]
        self.molarStr        = str(leapParams["molarStr"])
        self.negativeIon     = leapParams["positiveIon"]
        self.positiveIon     = leapParams["negativeIon"]
        self.iscomputed      = False
        self.igb             = leapParams["igb"]
        self.tleapfilename = "tleap.in"
    
        print("Loaded Tleap maker")
    #Builds a TLEAP inputfile using template and list of input parameters
    def buildLeapFile(self):
        print("Building leap.in")
        #Build commands for each line
        source      = ""
        loadoff     = ""
        amberparams = ""
        amberprep   = ""
        trans  = ""
        
        #Add Sources
        for d in self.leapSources:
            if 'leaprc' in d:
                source += 'source '+d+"\n"

            if '.lib' in d:
                loadoff += 'loadoff '+d+"\n"
            
            if 'frcmod' in d:
                amberparams += "loadamberparams "+d+"\n"

        #Add AuxFiles
        for d in self.leapFiles:
            if '.off' in d:
                loadoff += 'loadoff '+d+"\n"

            if 'frcmod' in d:
                amberparams += "loadamberparams "+d+"\n"

            if '.prep' in d:
                amberprep += "loadamberprep "+d+"\n"

        #Add AtomTypes custom definitions
        if self.addAtomTypes != "":
            addatomtypes = "addAtomTypes " + self.addAtomTypes
        else:
            addatomtypes = ""
        
        #Add Custom Bonds
        if self.bondInfo != "":
            bondInfo = self.bondInfo.replace("\\r\\n","\n")
        else:
            bondInfo = ""
            
        #print(source)
        #print(loadoff)
        #print(amberparams)
        #print(amberprep)
        
        #IGB Options for bond radii
        if int(self.igb) == 8:
            bondRadiiString = "set default PBradii mbondi3"
        else:
            bondRadiiString = ""
        
        #Define replacement keywords and content for template
        REPLACEMENTS = [
            ("{{sources}}", source),
            ("{{addAtomTypes}}", addatomtypes),
            ("{{offFiles}}", loadoff),
            ("{{amberPreps}}", amberprep),
            ("{{amberParams}}", amberparams),
            ("{{inputPdbFile}}", self.inputPdbFile),
            ("{{bondInfo}}", bondInfo),
            ("{{targetDirectory}}", self.targetDirectory),
            ("{{projectID}}", self.projectID),
            ("{{createDate}}", self.createDate),
            ("{{negativeIon}}", self.negativeIon),
            ("{{positiveIon}}", self.positiveIon),
            ("{{waterBoxModel}}", self.waterBoxModel),
            ("{{waterBoxDistance}}", self.waterBoxDistance),
            ("{{molarStr}}", self.molarStr),
            ("{{boxShape}}", self.boxShape),
            ("{{boxSize}}", self.boxSize),
            ("{{projectName}}", self.projectName),
            ("{{bondRadii}}", bondRadiiString)   
        ]
        
        #Replace definitions in template
        self.telapcontent = self.template
        for old, new in REPLACEMENTS:         
            self.telapcontent = self.telapcontent.replace(old, str(new))
        
        print("Tleap File computed correctly")
        self.iscomputed = True
        
                
    #Returns a tleapFile - False if not generated yet  
    def getLeapFile(self):
        if self.iscomputed:
            return self.telapcontent
        else:
            return False
        
    #Writes Tleapfile in project directory
    def writeLeapFile(self):
        if self.iscomputed:
            with open(self.targetDirectory+self.tleapfilename, "w+") as f:
                f.write(self.telapcontent)
            return self.targetDirectory+self.tleapfilename
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
"""
Creates a prototype of the wildtype input system - Represents a WT System - All actions upon it emanate from here

Functions: 
    - Mutate the original input structure of the project and save new complex in the project's mutant directory
    - Build the singlet, duplet and triplet dictionary of mutants using combinatorial operators
    - Calculate all initial mutants for a given Inputfile, using anchorpoint definitions of a project 
    - Create Initial input files for any project
    - Sets/gets Anchorpoints of the WT structure
    - Sets/gets Clusters of the WT structure
    - Sets/gets Molecular Objects of the WT structure
    - Converts residues from/to 1to3 letter code and backwards
        

Constructor:
        - InputSystem(projectID)

"""
class InputSystem():
    
    path          = "" #This is the path to the project folder - Must be set in the constructor
    projectID     = 0 #This is the ID of the project - Must be set in the constructor
    prmtop_file   = "receptor_ligand.prmtop" #this is the OpenMM input in all mutants
    inpcrd_file   = "receptor_ligand.inpcrd" #This is the OpenMM input in all mutants too
    pdb_hydrated  = "receptor_ligand_wat.pdb" #this is the hydrated and equilibrated template in all mutants
    pdb_dry       = "receptor_ligand.pdb" #This is how the template will lokk like in every mutant
    pdb_mutated   = "original_mutated.pdb" #This is how the template will lokk like in every mutant
    
    tleap_params  = {} #The tleap params for generating all inputs. Comes from the project in the DB. Same for all mutants
    tleap_file    = "tleap.in" #The name of the tleap file to be stored in every mutant's directory
        
    mutantpath = "" #the path to the mutant folder
    inputpath  = "" #the path to the input folder. Same for the entire project - both set in the constructor
    projectpath= "" #Path to the project directory
    
    mutants = {}
    
    #env = environ() #Boot modeller - once for generating all mutants
    #env.io.atom_files_directory = ['.', './atom_files']
    #env.libs.topology.read(file='$(LIB)/top_heav.lib') # Read the topology library
    #env.libs.parameters.read(file='$(LIB)/par.lib') #CHARRMM
    #COpy HEATATMs, mantain coordinates and parse instead of recreating
    #env.io.hetatm = True
    
    #A small hack... I hate loading biopython to do a 1to3 conversion...
    res3to1 = {'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K', 'ILE': 'I', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ASN': 'N', 'GLY': 'G', 'HIS': 'H', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W', 'ALA': 'A', 'VAL': 'V', 'GLU': 'E', 'TYR': 'Y', 'MET': 'M'}
    #Same as before, but backwards
    res1to3 = {v: k for k, v in res3to1.items()} 
    
    #CONSTRUCTOR of the INPUTSYSTEM
    def __init__(self, path, projectID, pdb_original_name="original.pdb"):
                
        #Set class self variables
        self.path        = path
        self.projectID   = projectID
        self.projectpath = f'{path}/{projectID}/'
        self.mutantpath  = f'{path}/{projectID}/mutants/'
        self.inputpath   = f'{path}/{projectID}/inputs/'
        self.outputpath  = f'{path}/{projectID}/outputs/'
        self.pdb_original_input = pdb_original_name
        self.anchorpoints = []
        #Create projectDirectories
        self.createProjectDirectories()  
    
    
    
    def createProjectDirectories(self):
        #1 - Create project directories
        #----------------------------------------
        if not os.path.exists(self.projectpath):
            print(f'Making folder: {self.projectpath}')
            os.makedirs(self.projectpath)
            
        if not os.path.exists(self.mutantpath):
            print(f'Making folder: {self.mutantpath}')
            os.makedirs(self.mutantpath)
            
        if not os.path.exists(self.inputpath):
            print(f'Making folder: {self.inputpath}')
            os.makedirs(self.inputpath)
            
        if not os.path.exists(self.outputpath):
            os.makedirs(self.outputpath)
        #----------------------------------------
        
   
    
    #return a Leap config skeleton, based on provided params
    #This is called from MD node
    
    #TODO - PENDING CREATING THIS FROM HERE PROPERLY - CALLED FROM MD NODE (for mutant creation)
    def buildLeapDict(self, projectid="1", dirp='', mutantid=0, project={}):
        inputs   = project["inputs"]
        analysis = project["analysis"]
        
        #Check which file should be read as input. The original, or the mutated original.
        #This depends on mutant=0 or any other mutant. Meaning wildtype or any mutated decoy
        if mutantid != 0:
            inputpdbfilename = "original_mutated.pdb" #We tell TLEAP to pick the mutated PDB from inside the mutant folder
        else:
            inputpdbfilename = "original.pdb" #We keep it to the original
            
        #Define energy type
        energy = "energy_gbsa"
        if "energy_pbsa" in analysis:
            energy = "energy_pbsa"

        leap = {
          "projectID"    : projectid,
          "projectName"  : project['project_name'],
          "mutantID"     : str(mutantid),
          "createDate"   : date.today().strftime('%Y-%m-%d'),
          "targetDirectory": f'{dirp}/',
          "leap_sources": inputs["leapSourcesContent"] ,
          "leap_files":   inputs["leapSources"],
          "inputPdbFile": inputpdbfilename ,
          "addAtomTypes": inputs['leapAtomTypes'],
          "bondInfo":     inputs['leapBonds'],
          "leapSourcesDirectory": "",
          "boxShape":     inputs['shapeLeapWaterbox'],
          "watModel":     inputs['leapWaterbox'],
          "boxSize":      inputs['leapWaterboxSize'],
          "positiveIon":  inputs['leapPositiveIon'],
          "negativeIon":  inputs['LeapNegativeIon'],
          "molarStr":     inputs['leapmolarStrength'],
          "igb":          inputs["igb"],
          "inp":          inputs["inp"],
          "energy":       energy
        }
        print("Generated TLEAP template filler for project "+str(projectid))
        return leap       
    
        
    
    def createTleapScriptandInputs(self, leapParams, mutantID=0, selectors= {}):
        #mutant 0 means wildtype. This goes in the toplevel inputs directory
        print("Generating TLEAP File")
        s = tleapGen(leapParams, self.projectpath, self.projectID, mutantID)
        s.buildLeapFile()
        file = s.writeLeapFile()
        
        #runtleap and create project/mutant inputs
       
        #TODO Figure out a way to have conda add the right paths to Ambertools21 tleap
        #This is shitty, because ambertools installed via conda adds a PATH to its /bin upon activation, and python shells don't activate the conda env
        print("WARNING: Tleap is being defined with an absolute path to the local environment - Remember to make tleap executable be available globally before distributing")
        run([f'tleap -I {self.inputpath} -f {file}'], bufsize=2048, stdin=PIPE, shell=True, executable='/bin/bash')
        
        
        #PEDRO - MARCH 6 2023
        #Create Receptor and Ligand prmtops with tleap output prmtop of the complex
        path = self.projectpath
        
        #should work for wildtype and every mutant
        if mutantID == 0:
            targetdir = f'{path}/inputs/'
        else:
            targetdir = f'{path}/mutants/{mutantID}/inputs/'
        
        #If files exist
        if os.path.isfile(targetdir+self.prmtop_file):
            if os.path.isfile(targetdir+self.inpcrd_file):
                for name, selector in selectors.items():
                    
                    #TODO: REMEMBER - Since splitting with parmed is not working by selecting the residues, selector must be subtracted or sliced
                    #from the input to create the oposite chunk of system. Selector for ligand and receptor should be inverted for now.
                    
                    #THIS IS A TEMPORARY WORKAROUND WHILE JASON SWAILS FIGURES HOW TO FIX PARMED TO PRESERVE OFF DIAGONAL BONDS DURING PRMTOP SPLITTING
                    #MEANWHILE WE USE STRIP() instead of SPLIT()
                    if name == 'ligand':
                        name = 'receptor'
                    else:
                        name = 'ligand'
                     
                    file = pm.load_file(targetdir+self.prmtop_file, xyz=targetdir+self.inpcrd_file)
                    file.strip(selector) #residues to delete from input file 
                    file.write_parm(targetdir+name+".prmtop")
                
                print("Generated receptor,prmtop and ligand.prmtop into "+targetdir)
        else:
            print("Something went wrong. TLEAP prmtop not found in "+targetdir+". Unable to split and generate ligand/receptor files")
              
    
    
    #Returns the list of allowed residues that a given anchor point can mutate into (comes from GUI)
    def getMutableMatrix(self, anchor):
        matrix = []
        for resi in self.anchorpoints:
            if(resi["resno_NGL"] == int(anchor)):
                #print(resi["mutable_into"])
                for res in resi["mutable_into"]:
                    cha = resi["chain"]
                    matrix.append({f'{cha}:{anchor}': res})
                return matrix
        return None
    
    
    
    #Return a dictionary of all possible singlets, duplets and triplets per cluster    
    #Clusters and anchorpoints should exist
    def buildMutants(self): 
        index = 0
        idmutant = 1
        mut  = []
        print("Generating combinatorial operations for project")
        #Generate lists of mutations per position for each position of a cluster
        mut.append({"id_project": self.projectID, "status": 'pending', "mutantID": idmutant, "mutant": [], "combination": "wildtype", "cluster": index, "type": "initial"}) #TODO - NOT TESTED IN PRODUCTION - JULY2023 tested
        
        for cluster in self.clusters:
            index +=1
            
            positionslist = []
            mutants_so_far = []
            
            #Generate list array of all elements of the cluster into their allowed residues
            for ele in cluster:
                positionslist.append(self.getMutableMatrix(ele))
            
            #Generate Singlets (uses itertools)
            for singlets in list(combinations(positionslist,1)):
                for combi in list(product(*singlets)):
                    idmutant +=1
                    mutantstring = ""
                    
                    #PREVENT DUPLICATES FROM OTHER CLUSTERS - JULY 2023 - NOT TESTED
                    dic = next(iter(combi[0]))
                    v1 = combi[0][dic]
                    
                    mutantstring = str(dic+v1)
                    if mutantstring not in mutants_so_far:
                        mutants_so_far.append(mutantstring)
                        mut.append({"id_project": self.projectID, "status": 'pending', "mutantID": idmutant, "mutant": {dic: v1}, "combination": "singlet", "cluster": index, "type": "initial"})
                        #mut.append({"id_project": self.projectID, "status": 'pending', "mutantID": idmutant, "mutant": combi, "combination": "singlet", "cluster": index, "type": "initial"})
                    else:
                        print("Excluding duplicate "+mutantstring)
                
            #Generate Duplets - Nasty.. but gets the job done 
            for duplets in list(combinations(positionslist,2)):
                for combi in list(product(*duplets)):
                    idmutant +=1
                    mutantstring = ""
                    
                    dic = next(iter(combi[0]))
                    dic2 = next(iter(combi[1]))
                    v1 = combi[0][dic]
                    v2 = combi[1][dic2]
                    
                    mutantstring = str(dic+v1+dic2+v2)
                    #TODO: PREVENT DUPLICATES FROM OTHER CLUSTERS
                    if mutantstring not in mutants_so_far:
                        mutants_so_far.append(mutantstring)
                        mut.append({"id_project": self.projectID, "status": 'pending', "mutantID": idmutant, "mutant": {dic: v1, dic2: v2}, "combination": "duplet", "cluster": index, "type": "initial"})
                    else:
                        print("Excluding duplicate "+mutantstring)
                    
            #Generate Triplets - Nasty.. but gets the job done
            for triplets in list(combinations(positionslist,3)):
                for combi in list(product(*triplets)):
                    idmutant +=1
                    mutantstring = ""
                    
                    dic = next(iter(combi[0]))
                    dic2 = next(iter(combi[1]))
                    dic3 = next(iter(combi[2]))
                    v1 = combi[0][dic]
                    v2 = combi[1][dic2]
                    v3 = combi[2][dic3]
                    
                    mutantstring = str(dic+v1+dic2+v2+dic3+v3)
                    #TODO: PREVENT DUPLICATES FROM OTHER CLUSTERS
                    if mutantstring not in mutants_so_far:
                        mutants_so_far.append(mutantstring)
                        mut.append({"id_project": self.projectID, "status": 'pending', "mutantID": idmutant, "mutant": {dic: v1, dic2: v2, dic3: v3}, "combination": "triplet", "cluster": index, "type": "initial"})
                    else:
                        print("Excluding duplicate "+mutantstring)
        #mutation = {'chain', pos): newres}
        print(f'Generated {idmutant} total mutants for project.. saving')
        self.mutants = mut
        return mut
            
        
    #Extracts mutable residues from residuemap
    def setAnchorPoints(self, residuemap):
        anchors = []
        for chain, content in residuemap.items():
            for residue in content:
               if residue is not None:
                   if residue["isanchor"]:
                       anchors.append(residue)                       
        #Store anchorpoints in class variable
        self.anchorpoints = anchors



    
    #GET ANCHORPOINTS
    def getAnchorPoints(self):
        return self.anchorpoints
    


    
    #SET CLUSTERS
    def setClusters(self, clustermap):
        clusters = []
        for cluster in clustermap:
            if cluster is not None:
                 clusters.append(cluster)      
        self.clusters = clusters
    
        
    
    #GET CLUSTERS
    def getClusters(self):
        return self.clusters
    
    
    
    def buildMutantFromWildType(self, mutations, mutantID):
       #Takes wildtype PDB system for the current project. Creates new mutant, given a mutation list
       #mutations = {cha:pos : 'res', cha:pos : 'res'} - This is the expected format of the mutations parameter
       #mutantID is the mutant ID in the database. A folder will be created.
       
       #TODO - SUPER IMPORTANT
       #DYME DISTRIBUTABLE MUST PATCH THE FILE modlib/restyp.lib and delete the ZN alias, so the modeller 
       #same goes for CYS
       #leaves the ZN atom names untouched, else tleap fails later if the original PDB contains Zinc+2
       
       env = environ() #Boot modeller - once for generating all mutants
       env.io.atom_files_directory = ['.', './atom_files']
       env.libs.topology.read(file='$(LIB)/top_heav.lib') # Read the topology library
       env.libs.parameters.read(file='$(LIB)/par.lib') #CHARRMM
       
       pdb_file = self.inputpath+self.pdb_original_input
       print(f'Loading mutant PDB file from inputs at: {pdb_file}')
       
       #Output file
       output_dir  = f'{self.mutantpath}/{mutantID}/inputs/'
       output_file = f'{self.mutantpath}/{mutantID}/inputs/{self.pdb_mutated}'
       
       #check if mutant folder already exist, else, create it
       if not os.path.exists(self.mutantpath):
           os.makedirs(self.mutantpath)
    
       if not os.path.exists(self.mutantpath+"/"+str(mutantID)):
           os.makedirs(self.mutantpath+"/"+str(mutantID))
       
       if not os.path.exists(output_dir):
           os.makedirs(output_dir)
       
       print(f'Creating mutant output directories at: {output_dir}')
       print(f'Setting output file to: {output_file}')
       
     
       #Prepare Modeller
       mdl = model(env, file=pdb_file)
       aln = alignment(env)
       aln.append_model(mdl, atom_files=pdb_file, align_codes=pdb_file)
       
       print(f'generating mutant with list {mutations}')
       
       # Iterate over the mutations and mutate each residue
       
       for mutation in mutations:
           for pos, new_residue in mutation.items():
               chain_id, res_id = pos.split(":")
               pointmut = f'{res_id}:{chain_id}'
               sel = selection(mdl.residues[pointmut])
               sel.mutate(residue_type=self.res1to3[new_residue]) #mutate
           
       ################################################################################
       aln.append_model(mdl, align_codes='mut') # Add the mutated sequence to the alignment arrays
       mdl.clear_topology()
       mdl.generate_topology(aln['mut'])
    
       mdl.transfer_xyz(aln) # Transfer all the coordinates you can from the template native structure
       mdl.build(initialize_xyz=False, build_method='INTERNAL_COORDINATES')
       #mdl.patch_ss()
       #mdl.patch_ss_templates(aln) #Make sure the CONECT records are added for any disulphides
       print("GENERATING DISULPHIDES IF ANY---------------------------------------------------------------!!")
       mdl2 = model(env, file=pdb_file)
       # Generate the mutated model
       mdl.res_num_from(mdl2,aln)
       # Write the new structure to a PDB file
       
       mdl.write(file=output_file, model_format='PDB')
       #TODO: ENSURE THE FUCKING PDB (WILDTYPE) HAS EVERY ATOM ASSIGNED TO A CHAIN, ELSE, 
       #THE STUPID MODELLER INSERTS A TER AND THE LIGAND/RECEPTOR PRMTOP'S WILL HAVE AN 
       #ATOM COUNT MISMATCH IN RELATION TO THE PRMTOP OF THE COMPLEX!!!. IT WILL BREAK MMGBSA
       
       return output_file







"""
Creates a VMD loading template for DYME UI

Constructor:
        - vmdloader(tleapParams)

"""     
class vmdLoader:
    
    template = """display resetview
mol new {TRAJECTORY} type {netcdf} first 0 last -1 step 1 waitfor all
mol addfile {PRMTOP} type {parm7} first 0 last -1 step 1 waitfor all
display projection Orthographic
display depthcue off
mol addrep 0

mol modselect 0 0 all and noh and not water
mol color Name
mol selection all and noh and not water
mol material Opaque

mol modstyle 1 0 NewCartoon 0.300000 10.000000 4.100000 0
mol color Name
mol selection all and noh and not water
mol material Opaque

mol modstyle 2 0 HBonds 3.500000 30.000000 1.000000

mol smoothrep 0 0 20
mol smoothrep 0 1 20
mol smoothrep 0 2 20

animate style Loop
animate goto start
animate forward

"""   
    #SET INITIAL VARS
    def __init__(self, traj_path, prmtop_path, out_path, projectid, mutantID):  
        
        self.vmdcontent = ""
        self.buildVMDload(traj_path, prmtop_path, out_path)
        self.writeLeapFile(out_path)
        self.projectid = projectid
        self.mutantID = mutantID
        
    #Builds a TLEAP inputfile using template and list of input parameters
    def buildVMDload(self,traj_path, prmtop_path, out_path):
        
        #GET Important Waters
        #wat = db.dbtable_processed_data.find_one({"id_project": int(self.projectid), "mutantID": self.mutantID},{"water_ids.important_waters": 1})
        #aguas = []
        #for mol in wat ["water_ids"]["important_waters"]:
        #  aguas.append(wat["water_ids"]["important_waters"][mol]["residue"])
        #water_resids = " ".join([a[3:].split("-O")[0] for a in aguas])
        
        REPLACEMENTS = [
            ("TRAJECTORY", traj_path),
            ("PRMTOP", prmtop_path)
            #,("WATERS", aguas)
        ]
        
        #PENDING TO ADD MODSTYLE FOR WATERS IN TEMPLATE - PEDRO 2024 FEB
        
        #Replace definitions in template
        self.vmdcontent = self.template
        for old, new in REPLACEMENTS:         
            self.vmdcontent = self.vmdcontent.replace(old, str(new))

    #Writes Tleapfile in project directory
    def writeLeapFile(self, out_path):
        with open(out_path, "w+") as f:
                f.write(self.vmdcontent)
        
