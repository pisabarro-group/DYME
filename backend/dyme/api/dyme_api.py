# -*- coding: utf-8 -*-
"""
DYME - Dynamic Mutagenesis Engine

File:           dyme_api.py
Description:    RESTful API entry point - GUI calls @app.routed functions with 
                client side JS - always answers in JSON.

Purpose:        Hooks to WSGI server via Apache2 - Called from dyme_api.wsgi
                (See /etc/apache2/sites-enabled/dyme_api.conf)
                
                Some of the functions here were mirrored from Peter Eastman's 
                openmm-setup package.. we only used flask to provide an API, 
                not the whole Django app. API Our server hooks via Apache2.
                
                WARNING !!
                mod_wsgi shared libraries for apache2 have to be compiled
                for the exact same version of python in the CONDA environment
                where DYME lives. Else, there is no communication between python 
                in conda from WSGI module of apache2.
                
                Make sure to add mod_wsgi package to anaconda and move the shared .so 
                libraries to the local server LD_PATH (/usr/lib64 or whatever)

Author:     
Pedro Manuel Guillem Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>
Structural Bioinformatics Lab - BIOTEC - Pisabarro Group
Technische Universität Dresden
"""

__author__ = "Pedro M. Guillem-Gloria"
__version__ = "0.1"

#3RD PARTY
import openmm as mm
import openmm.unit as unit
from openmm.app import PDBFile, PDBxFile
from pdbfixer.pdbfixer import PDBFixer, proteinResidues, dnaResidues, rnaResidues, _guessFileFormat
from flask import Flask, request, session, g, make_response, send_file, url_for, send_from_directory, Response, current_app
from werkzeug.utils import secure_filename


#SYSTEM
#Logging
import sys
sys.stdout = sys.stderr
from multiprocessing import Process, Pipe
from math import sqrt
import datetime
from io import StringIO 
import os
import shutil
#import signal
import tempfile
#import threading
import time
#import traceback
#import webbrowser
#import zipfile
import json
from bson import BSON
from pprint import pprint
from datetime import date
from bson.json_util import dumps
import pandas as pd
#import logging
import functools

#Ours
sys.path.append('/dyme_base/backend/dyme')
from DymeDB import DymeDB
from DymeTools import tleapGen, InputSystem, vmdLoader



# python 2 and 3 compatibility
try:
    basestring  # attempt to evaluate basestring
    def isstr(s):
        return isinstance(s, basestring)
except NameError:
    def isstr(s):
        return isinstance(s, str)



#FLASK STUFF
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = "fb05431127ead66f46f9b0a4894d1727836b902d71d4034dc12d428204678814"
app.jinja_env.globals['mm'] = mm
db = DymeDB("localhost")


#WIZARD STUFF - Public variables
uploadedFiles = {} #Holds uploaded files from the user
fixer = None
scriptOutput = None
simulationProcess = None
response = {"action": "", "component": "", "response": "" }
pfile = None
pname = None

#COMMON STRUCTURES
#Non Naturals Trial
#    'LEN': '⅃',
#    '2NP': 'ℵ',
#    'PRC': 'ϸ',
#    'CIT': '⅌',
#    '55C': "X",
#    'S55': "X",
#    'R86': "Z",

res3to1 = {'CY4': 'C', 'CY1': 'C','CY2': 'C','CY3': 'C','CYS': 'C', 'CYX': 'C',
  'HD1': 'H', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K',
  'ILE': 'I', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ASN': 'N',
  'GLY': 'G', 'HIS': 'H', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W', 
  'ALA': 'A', 'VAL': 'V', 'GLU': 'E', 'TYR': 'Y', 
  'MET': 'M', 'HIE':'H', 'HID': 'H',  'HIP': 'H', 'HD2': 'H',
  'DA': 'A', 'DT':'T', 'DG': 'G',  'DC': 'C',
  'LEN':'L','2NP':'ℵ','PRC':'ϸ','CIT':'⅌','55C':'X','S55':'X','R86':'Z'}

#reverse function
res1to3 = {v: k for k, v in res3to1.items()}

#ProteinAlphabet aminoacids in the correct order (see logojs github)
allaminos = ["A","B","C","D","E","F","G","H","I","K","L","M","N","P","Q","R","S","T","V","W","X","Y","Z"]

#Possible Categorical features
possible_values = {
    'Bulkiness': ["Tiny", "Small", "Long", "Bulky"],
    'Geometry': ["Aromatic", "Linear"],
    'Chemistry': ["Charged", "Polar", "Hydrophobic"],
    'Polarity': ["Negative", "Positive", "Neutral", "Uncharged"],
    'HBond': ["Donor", "Acceptor", "Both", "None"],
    'HasSulfur': ["Yes", "No"],
    '1LetterCode': allaminos
}

#Define which categories is the AI going to use to build the encoders
activeCategories = ['Bulkiness', 'Polarity', 'Chemistry', 'Hbond', '1LetterCode']

#Categorical features per residue
aminoproperties = {
	"ALA": {"Bulkiness": "Tiny",  "Geometry": "Linear",   "Chemistry": "Hydrophobic", "Polarity": "Uncharged","1LetterCode": "A", "Hbond": "None",     "HasSulfur": "No" },
	"CYS": {"Bulkiness": "Tiny",  "Geometry": "Linear",   "Chemistry": "Polar",       "Polarity": "Neutral",  "1LetterCode": "C", "Hbond": "None",     "HasSulfur": "Yes" },
    "CY1": {"Bulkiness": "Tiny",  "Geometry": "Linear",   "Chemistry": "Polar",       "Polarity": "Neutral",  "1LetterCode": "C", "Hbond": "None",     "HasSulfur": "Yes" },
    "CY2": {"Bulkiness": "Tiny",  "Geometry": "Linear",   "Chemistry": "Polar",       "Polarity": "Neutral",  "1LetterCode": "C", "Hbond": "None",     "HasSulfur": "Yes" },
    "CY3": {"Bulkiness": "Tiny",  "Geometry": "Linear",   "Chemistry": "Polar",       "Polarity": "Neutral",  "1LetterCode": "C", "Hbond": "None",     "HasSulfur": "Yes" },
    "CY4": {"Bulkiness": "Tiny",  "Geometry": "Linear",   "Chemistry": "Polar",       "Polarity": "Neutral",  "1LetterCode": "C", "Hbond": "None",     "HasSulfur": "Yes" },    
    "CYX": {"Bulkiness": "Tiny",  "Geometry": "Linear",   "Chemistry": "Polar",       "Polarity": "Neutral",  "1LetterCode": "C", "Hbond": "None",     "HasSulfur": "Yes" },
    "CSS": {"Bulkiness": "Tiny",  "Geometry": "Linear",   "Chemistry": "Polar",       "Polarity": "Neutral",  "1LetterCode": "C", "Hbond": "None",     "HasSulfur": "Yes" },
	"ASP": {"Bulkiness": "Small", "Geometry": "Linear",   "Chemistry": "Charged",     "Polarity": "Negative", "1LetterCode": "D", "Hbond": "Acceptor", "HasSulfur": "No" },
	"GLU": {"Bulkiness": "Long",  "Geometry": "Linear",   "Chemistry": "Charged",     "Polarity": "Negative", "1LetterCode": "E", "Hbond": "Acceptor", "HasSulfur": "No" },
	"PHE": {"Bulkiness": "Bulky", "Geometry": "Aromatic", "Chemistry": "Hydrophobic", "Polarity": "Uncharged","1LetterCode": "F", "Hbond": "None",     "HasSulfur": "No" },
	"GLY": {"Bulkiness": "Tiny",  "Geometry": "Linear",   "Chemistry": "Neutral",     "Polarity": "Uncharged","1LetterCode": "G", "Hbond": "None",     "HasSulfur": "No" },
	"HIS": {"Bulkiness": "Bulky", "Geometry": "Aromatic", "Chemistry": "Polar",       "Polarity": "Positive", "1LetterCode": "H", "Hbond": "Both",     "HasSulfur": "No" },
    "HIE": {"Bulkiness": "Bulky", "Geometry": "Aromatic", "Chemistry": "Polar",       "Polarity": "Positive", "1LetterCode": "H", "Hbond": "Both",     "HasSulfur": "No" },
    "HID": {"Bulkiness": "Bulky", "Geometry": "Aromatic", "Chemistry": "Polar",       "Polarity": "Positive", "1LetterCode": "H", "Hbond": "Both",     "HasSulfur": "No" },
    "HIP": {"Bulkiness": "Bulky", "Geometry": "Aromatic", "Chemistry": "Polar",       "Polarity": "Positive", "1LetterCode": "H", "Hbond": "Both",     "HasSulfur": "No" },   
    "HD1": {"Bulkiness": "Bulky", "Geometry": "Aromatic", "Chemistry": "Polar",       "Polarity": "Positive", "1LetterCode": "H", "Hbond": "Both",     "HasSulfur": "No" },   	
    "HD2": {"Bulkiness": "Bulky", "Geometry": "Aromatic", "Chemistry": "Polar",       "Polarity": "Positive", "1LetterCode": "H", "Hbond": "Both",     "HasSulfur": "No" },   	    
    "ILE": {"Bulkiness": "Long",  "Geometry": "Linear",   "Chemistry": "Hydrophobic", "Polarity": "Uncharged","1LetterCode": "I", "Hbond": "None",     "HasSulfur": "No" },
	"LYS": {"Bulkiness": "Long",  "Geometry": "Linear",   "Chemistry": "Charged",     "Polarity": "Positive", "1LetterCode": "K", "Hbond": "Donor",    "HasSulfur": "No" },
	"LEU": {"Bulkiness": "Long",  "Geometry": "Linear",   "Chemistry": "Hydrophobic", "Polarity": "Uncharged","1LetterCode": "L", "Hbond": "None",     "HasSulfur": "No" },
	"MET": {"Bulkiness": "Long",  "Geometry": "Linear",   "Chemistry": "Hydrophobic", "Polarity": "Neutral",  "1LetterCode": "M", "Hbond": "None",     "HasSulfur": "Yes" },
	"ASN": {"Bulkiness": "Small", "Geometry": "Linear",   "Chemistry": "Polar",       "Polarity": "Neutral",  "1LetterCode": "N", "Hbond": "Both",     "HasSulfur": "No" },
	"PRO": {"Bulkiness": "Small", "Geometry": "Linear",   "Chemistry": "Hydrophobic", "Polarity": "Neutral",  "1LetterCode": "P", "Hbond": "None",     "HasSulfur": "No" },
	"GLN": {"Bulkiness": "Long",  "Geometry": "Linear",   "Chemistry": "Polar",       "Polarity": "Neutral",  "1LetterCode": "Q", "Hbond": "Both",     "HasSulfur": "No" },
	"ARG": {"Bulkiness": "Long",  "Geometry": "Linear",   "Chemistry": "Charged",     "Polarity": "Positive", "1LetterCode": "R", "Hbond": "Donor",    "HasSulfur": "No" },
	"SER": {"Bulkiness": "Tiny",  "Geometry": "Linear",   "Chemistry": "Polar",       "Polarity": "Neutral",  "1LetterCode": "S", "Hbond": "Both",     "HasSulfur": "No" },
	"THR": {"Bulkiness": "Small", "Geometry": "Linear",   "Chemistry": "Polar",       "Polarity": "Neutral",  "1LetterCode": "T", "Hbond": "Both",     "HasSulfur": "No" },
	"VAL": {"Bulkiness": "Small", "Geometry": "Linear",   "Chemistry": "Hydrophobic", "Polarity": "Uncharged","1LetterCode": "V", "Hbond": "None",     "HasSulfur": "No" },
	"TRP": {"Bulkiness": "Bulky", "Geometry": "Aromatic", "Chemistry": "Hydrophobic", "Polarity": "Neutral",  "1LetterCode": "W", "Hbond": "Donor",    "HasSulfur": "No" },
	"TYR": {"Bulkiness": "Bulky", "Geometry": "Aromatic", "Chemistry": "Polar",       "Polarity": "Neutral",  "1LetterCode": "Y", "Hbond": "Both",     "HasSulfur": "No" }
    } #PENDING NON STANDARD DEFINITIONS TO EXPORT DATAFRAMES HOT ENCODING FOR MACHINE LEARNING

    #Dictionary of DNA atoms
dna_atoms = {
        'DA': {
            'ring': ['N1', 'N3', 'C5', 'N6', 'N7'],
            'backbone': ['P', 'OP1', 'OP2', 'O5', 'C3', 'O3', 'O4']
        },
        'DT': {
            'ring': ['N1', 'O2', 'N3', 'O4'],
            'backbone': ['P', 'OP1', 'OP2', 'O5', 'O3', 'O4']
        },
        'DC': {
            'ring': ['N1', 'O2', 'N3', 'N4'],
            'backbone': ['P', 'OP1', 'OP2', 'O5', 'O3', 'O4']
        },
        'DG': {
            'ring': ['N1', 'N2', 'N3', 'N7', 'O6', 'N9'],
            'backbone': ['P', 'OP1', 'OP2', 'O5', 'O3', 'O4']
        }
    }

protein_atoms = ['N', 'CA', 'C', 'O']

#MDSRV STUFF
struct = []
MODULE_DIR = os.path.split( os.path.abspath( __file__ ) )[0]
DATA_DIRS = {
     "dyme": os.path.abspath("/dyme_root/projects/") #WE MUST POPULATE THIS FROM THE DATABASE
}




#actions = redraw|execjs|
#component_name = name of DIV object
#response = Response content


#HELPER FUNCTIONS FOR WIZZARD
def saveUploadedFiles():
    uploadedFiles.clear()
    for key in request.files:
        filelist = []
        for file in request.files.getlist(key):
            temp = tempfile.TemporaryFile()
            shutil.copyfileobj(file, temp)
            filelist.append((temp, secure_filename(file.filename)))
        uploadedFiles[key] = filelist

    print(f"{uploadedFiles}")

#Create a new project in the database
def createDymeProjectDatabase():
   pass 

#Convert seconds to human readable format
def display_time(seconds, granularity=2):
        """
        Computes Weeks, Days, Hours, Minutes, Seconds
        given a number of seconds. Author: Mr. B
        """
        intervals = (
            ('weeks', 604800),  # 60 * 60 * 24 * 7
            ('days', 86400),    # 60 * 60 * 24
            ('hours', 3600),    # 60 * 60
            ('minutes', 60),
            ('seconds', 1),
        )
        
        result = []
        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(value, name))
                
        return ', '.join(result[:granularity])


#GET Available leap sources. uses the path to the environment
@app.route("/getLeapSources")
def getLeapSources():
    options = "<option value='0'>Select to add...</option>"
    pathleap = "/dyme_env/anaconda/envs/dyme_main/dat/leap/" #Remember to change this for whatever path leap has on the ambertools package of the env
    relevant = ["cmd","parm","lib"]
    for dir in sorted(os.listdir(pathleap), key=str.lower):
        if dir in relevant:
            if dir == "cmd":
                options += "<optgroup label='Amber Forcefields'>"
            if dir == "parm": 
                options += "<optgroup label='Amber Params'>"
            if dir == "lib": 
                options += "<optgroup label='Amber Libs'>"
                
            for file in os.listdir(pathleap+dir):
                if ("pycache" not in file) and (".dat" not in file) and (".py" not in file):
                  options += "<option value='"+file+"'>"+file+"</option>\n" 
                
            options += "</optgroup>"   
    #Response to the website        
    res = {
        "action": "fillLeapOptionsSelect",
        "component": "",
        "response": options
    } 
    return json.dumps(res)




#Load PDB File from Wizzard, project name, water model and forcefield.
@app.route("/step1", methods=['POST'])
def wizzardStep1():
    
  sourcetype = request.form.get('sourcetype', '')
  session['sourcetype'] = sourcetype
  
  #DEFAULT ERROR
  res = {
      "action": "showmessage",
      "component": "wizzardModal",
      "response": "Flask Error uploading files: "+sourcetype
  }
  
  print(f"Initiating WizardStep1 with PDB type {sourcetype}")
  
  global fixer
  global pfile
  
  #SOURCE TYPE PDB
  #THIS IS STILL PENDING. THE ONLY SUPPORTED WAY TO CREATE SYSTEM RIGHT NOW IS TLEAP
  if sourcetype == "pdb":
      #Get File and store in temp
      
      
      if 'pdbFile' not in request.files:
        # No file was sent in request
        res = {
            "action": "showmessage",
            "component": "wizzardModal",
            "response": "Flask Error uploading files"
        }
    
        #Save uploaded file in a temp   
        saveUploadedFiles()
        
        #Set session variables in Flask
        session['project_name'] = request.form.get('projectName', '')
        session['forcefield']   = request.form.get('inputForcefield', '')
        session['waterModel']   = request.form.get('inputFWater', '')
        #Set session Filename
        file, name = uploadedFiles['pdbFile'][0]
        file.seek(0, 0)
        session['pdbType'] = _guessFileFormat(file, name)
        
        #Create global fixer object
        
        if session['pdbType'] == 'pdb':
           fixer = PDBFixer(pdbfile=file)
        else:
           fixer = PDBFixer(pdbxfile=StringIO(file.read().decode()))
           
        #Move to step2 and show chains
        #Clientside JS manages display
        res = {
             "action": "gotoStep2",
             "component": "all",
             "response": "User File Uploaded!!"
        }
        
  
    
  #SOURCE TYPE AMBER - This should accept everything for the TLEAP script generation
  elif sourcetype == "amber":
           
      #1Check if PDB topology was selected
      if 'leadPdbFile' not in request.files:
         #user must upload a PDB, else stop
         res = {
             "action": "showmessage",
             "component": "wizzardModal",
             "response": "There was an error uploading your PDB file. Try again."
         }
             
      #1Check if the user uploaded any custom amber parameter files
      if 'leapFiles' in request.files:
        #save custom parameter files in project folder..
        hasCustomParams = True
      
      #Save Files Uploaded from the form
      saveUploadedFiles()
       
      #print(uploadedFiles['leapFiles'])
      #GET FORM VALUES
      
      #Project Name
      session['project_name']       = request.form.get('projectName', '')
      #Leap Bonds & Atomtypes
      session['leap_bonds']         = request.form.get('leapBonds', '')
      session['leap_atomtypes']     = request.form.get('leapAtomTypes', '')
      session["leap_sources"]       = request.form.getlist('leapSourcesContent')
      if hasCustomParams:
          session["leap_files"]     = [d[1] for d in uploadedFiles['leapFiles']]
      else:
          session["leap_files"] = []
        
      #Project Leap Variables
      session['box_shape']          = request.form.get('shapeLeapWaterbox', '')
      session['water_model']        = request.form.get('leapWaterbox', '')
      session['box_size']           = request.form.get('leapWaterboxSize', '')
      session['neutralize_pos_ion'] = request.form.get('leapPositiveIon', '')
      session['neutralize_neg_ion'] = request.form.get('LeapNegativeIon', '')
      session['molar_strength']     = request.form.get('leapmolarStrength', '')
      
      
      #print(session["leap_files"])
      #Save Input PDB File (#pfile is the BufferIO, #pname is the originalfilename)
      pfile, pname = uploadedFiles['leadPdbFile'][0]
      
      pfile.seek(0, 0)      
      session['pdbType'] = _guessFileFormat(pfile, pname)
      session["pdbName"] = pname
      
      
      #Clientside JS manages display
      res = {
             "action": "gotoStep3",
             "component": "all",
             "response": "Alles gut"
      }
    
  return json.dumps(res)


#Writes dictionary for TLEAP file creation
def buildLeapDict(projectid="1", dirp='', mutantid=0):
    
    #InputPDB file is always original.pdb, since the web api only triggers creating the wildtype
    
    leap = {
      "projectID"    : projectid,
      "projectName"  : session['project_name'],
      "mutantID"     : str(mutantid),
      "createDate"   : "0000-00-00",
      "targetDirectory": f'{dirp}/',
      "leap_sources": session["leap_sources"] ,
      "leap_files": session["leap_files"] ,
      "inputPdbFile": "original.pdb" ,
      "addAtomTypes": session['leap_atomtypes'],
      "bondInfo": session['leap_bonds'],
      "leapSourcesDirectory": "",
      "boxShape": session['box_shape'],
      "watModel": session['water_model'],
      "boxSize": session['box_size'],
      "positiveIon": session['neutralize_pos_ion'],
      "negativeIon": session['neutralize_neg_ion'],
      "molarStr": session['molar_strength'],
      "igb": session['igb']
    }
    return leap 

def buildSelectors(rmap, robject):
    selector = {}
    print(robject)
    for obj in robject:
        chain = obj['chains'][0]['key']
        res = []
        print(rmap)
        for residue in rmap[chain]:
            if residue != None:
                res.append(residue['resno_NGL'])
        sel = f':{res[0]}-{res[-1]}'
        
        if obj['mutable'] == True:
            selector['ligand'] = sel
        else:
            selector['receptor'] = sel
    return selector


#Comes from Openmm setup, returns an interpreted representation of the uploaded PDB structure.
@app.route('/getCurrentStructure')
def getCurrentStructure():
    #If we want pdbfixer to analyze the file and do stuff with it (Step2)
    if session['sourcetype'] == 'pdb':
        pdb = StringIO()
        PDBFile.writeFile(fixer.topology, fixer.positions, pdb)
        return pdb.getvalue()
    
    #If we are building from amber, just relay PDB contents back to the web UI (ngl)
    elif session['sourcetype'] == 'amber':
        pfile.seek(0,0)
        return pfile.read()
        #return 
        


#Load Simulation Options from wizzard Step2.
@app.route("/step2", methods=['POST'])
def wizzardStep2():
    pass




#Load Simulation Options from wizzard Step3.
@app.route("/step3", methods=['POST'])
def wizzardStep3():
    
    #ASSIGN Session variables with form variables
    session['nonbondedmethod']  = request.form.get('nonbondedmethod', '')
    session['ewaldTol']  = request.form.get('ewaldTol', '')
    session['cutoff']  = request.form.get('cutoff', '')
    session['constraints']  = request.form.get('constraints', '')
    session['constraintTol']  = request.form.get('constraintTol', '')
    
    session['dt']  = request.form.get('dt', '')
    session['pressure']  = request.form.get('pressure', '')
    session['ensemble']  = request.form.get('ensemble', '')
    session['temperature']  = request.form.get('temperature', '')
    session['friction']  = request.form.get('friction', '')
    
    
    session['steps']  = request.form.get('steps', '')
    session['equilibrationSteps']  = request.form.get('equilibrationSteps', '')
    session['platform']  = request.form.get('platform', '')
    session['precision']  = request.form.get('precision', '')
    #Add IGB 
    
    #Return success after validation and go to step 4
    res = {
         "action": "gotoStep4",
         "component": "all",
         "response": "User File Uploaded!!"
    }
    
    return json.dumps(res)
    


@app.route("/processNewProject", methods=['POST'])
def WizzardStep4():
    #print(request.get_data())
    #READ INPUT CONFIGURATION
   
    #Get new project settings
    newproject = json.loads(request.get_data())
     
    #Get default settings from DB and generate a new prroject ID (next ID)
    settings    = db.dbtable_default_settings.find_one({})

    #projectid  = db.dbtable_projects.count_documents({})+3 #This is suboptimal, fails if you delete a project in the middle.
    latest      = db.dbtable_projects.find_one({}, sort=[("id_project", -1)]) #This is better. Gets the latest project
    
    #If not the first project, increment top project id +1
    if latest is None:
        projectid = 1
    else:
        projectid   = int(latest["id_project"])+1
    
    #TODO- UNCOMMENT - DELETE INDEX
    #projectid = 1
    
    #Set paths from configfile (Settings)
    hdd_path = settings['hdd_path']
    pro_path = settings['project_dir']
    projdir  = f'{hdd_path}{pro_path}'
    namepr = newproject['inputs']['projectName']
    session['igb'] = newproject['inputs']["igb"] #Incude IGB value in Session for TLEAP (This is for later Scavenging purposes)
    session['inp'] = newproject['inputs']["inp"] #Incude INP value in Session for TLEAP (This is for later Scavenging purposes)
    
    today = date.today().strftime('%Y-%m-%d')
    unix = int(time.time()) 
    
    #From the Project Wizzard GUI
    project = {
            "id_project": projectid,
            "project_name": namepr,
            "project_folder": f'{projdir}/{projectid}',
            "date_created": today,
            "unix_timestamp": unix,
            "inputs": newproject['inputs'],
            "objects": newproject['objects']  ,
            "clusters": newproject['clusters'],
            "analysis": newproject['analysis'],
            "simulation": newproject['simulation'],
            "residuemap" : newproject['residuemap'],
    }
    
    project["inputs"]["leapSources"] = session["leap_files"]
    
    #print(project)
    #Insert Into projects DB
    
    #TODO- UNCOMMENT
    db.dbtable_projects.insert_one(project)
    
    #SaveCreate Dyme InputSystem object - This will create the project folders in the HHDD
    DymeSystem = InputSystem(projdir, projectid, "original.pdb")
    
    #Save original PDB and other input files in their expected directories
    #TODO - Verify all files are consistent.. support more than one PDB? verify not empty?
    try:
        for key in uploadedFiles:
            #Copy PDB file in original.pdb
            print(f'inspecting key {key}')
            if key == 'leadPdbFile':
                file, name = uploadedFiles[key][0]
                print('Writing PDB as original.pdb')
                file.seek(0, 0)
                with open(f'{projdir}/{projectid}/inputs/original.pdb', 'wb+') as outputFile:
                    shutil.copyfileobj(file, outputFile) 
                    
            #Copy TLEAP files in input folder    
            if key == 'leapFiles':
                for file, name in uploadedFiles[key]:
                    if name != '': #Fix. Must be not empty, else, the user didn't upload leap files or libs #PEDRO OCT 2024
                        print(f'Writing Tleapfile {name}')
                        file.seek(0, 0)
                        with open(f'{projdir}/{projectid}/inputs/{name}','wb+') as outputFile:
                            shutil.copyfileobj(file, outputFile)    
    except Exception as e:
        print(f"Exeption saving uploaded file: \n {e}")
        pass   
    
    
    #MARCH 6 2023
    #Create splitselectors (works with only 2 molecular objects currently)
    selectors = buildSelectors(newproject['residuemap'], newproject['objects']) #PENDING TO TEST LIVE!

    #Build tleap dictionary of parameters (from input options)
    leapDictCombined = buildLeapDict(str(projectid),projdir,0)
    #Build Tleap Script and run it 
    #splitselectors is simply a dictionary defining the Amber selectors to split the complex into ligand and receptor prmtops
    DymeSystem.createTleapScriptandInputs(leapDictCombined, 0, selectors)

    #Build All mutants
    #print(newproject['residuemap'])
    DymeSystem.setAnchorPoints(newproject['residuemap']) #This can come from the GUI of from the DB
    DymeSystem.setClusters(newproject['clusters']) #This can come from the GUI of from the DB

    #print(DymeSystem.anchorpoints)
    #print(DymeSystem.clusters)
    DymeSystem.buildMutants()
    db.dbtable_mutants.insert_many(DymeSystem.mutants) #Insert pending mutants into DB
    
    #TODO
    #Validate inputs... for now, we assume the GUI did this.
         
    res = {
        "action": "showmessage",
        "component": "wizzardModal",
        "response": f'Project {namepr} Created Successfully!'
    }
    return json.dumps(res)



def configureDefaultOptions():
    #Configure default simulation options based on water and forcefield
    #Some comes from Peter eastman's function from openmm-setup
    implicitWater = False
    if session['sourcetype'] == 'pdb' and session['waterModel'] == 'implicit':
        implicitWater = True
    isAmoeba = session['fileType'] == 'pdb' and 'amoeba' in session['forcefield']
    isDrude = session['fileType'] == 'pdb' and session['forcefield'].startswith('charmm_polar')
    session['ensemble']  = 'nvt' if implicitWater else 'npt'
    session['platform']  = 'CUDA' #Default... this is what we have at the BIOTEC
    session['precision'] = 'mixed'
    session['cutoff']    = '2.0' if implicitWater else '1.0'
    session['ewaldTol']  = '0.0005'
    session['constraintTol'] = '0.000001'
    session['hmr'] = True
    session['hmrMass'] = '1.5'
    if isAmoeba:
        session['dt'] = '0.002'
    elif isDrude:
        session['dt'] = '0.001'
    else:
        session['dt'] = '0.002'
    session['steps'] = '10000000'
    session['equilibrationSteps'] = '1000'
    session['temperature'] = '300' #Kelvins
    session['friction'] = '1.0'
    session['pressure'] = '1.0'
    session['barostatInterval'] = '25' #Steps
    session['nonbondedMethod'] = 'CutoffNonPeriodic' if implicitWater else 'PME'
    session['writeDCD'] = True
    session['dcdFilename'] = 'trajectory.dcd'
    session['dcdInterval'] = '10000'
    session['writeData'] = True
    session['dataFilename'] = 'log.txt'
    session['dataInterval'] = '1000'
    session['dataFields'] = ['step', 'speed' ,'progress', 'potentialEnergy', 'temperature']
    session['writeCheckpoint'] = True
    session['checkpointFilename'] = 'checkpoint.chk'
    session['checkpointInterval'] = '10000'
    session['writeSimulationXml'] = False
    session['systemXmlFilename'] = 'system.xml'
    session['integratorXmlFilename'] = 'integrator.xml'
    session['writeFinalState'] = False
    session['finalStateFileType'] = 'stateXML'
    session['finalStateFilename'] = "final_state.xml"
    session['igb']  = '2'
    session['totalframes'] = '1000'
    if isAmoeba:
        session['constraints'] = 'none'
    else:
        session['constraints'] = 'hbonds'
    if isAmoeba:
        session['constraints'] = 'none'
    else:
        session['constraints'] = 'hbonds'


#FLASK ROUTES - HANDLE HTTP REQUESTS & RESPOND
#RESPONSES ARE HANDLED & BY JAVASCRIPT ON CLIENTSIDE WITH JSON DECODE

#GET EXISTING PROJECT LIST FOR WEBSITE
@app.route("/getExistingProjects")
def getExistingProjects():
    #query for all projects
    projects = db.dbtable_projects.find({}, sort=[("id_project", -1)]) #PEDRO AUG 2024 - Add ordering by projectid
    
    res = {}
    projs = []
    
    
    if projects is not None:
        for project in projects:
            idp   = project['id_project']
            name  = project['project_name']
            date  = project['date_created']
            
            mutants  = db.dbtable_mutants.count_documents({'id_project': idp}) #get total mutants
            clusters = db.dbtable_mutants.find({'id_project': idp}).sort('cluster', -1).limit(1)[0]['cluster']; # get max clusters of project

            anchors = 0
            dummy = list()
            for cluster in project['clusters']:
                if cluster is not None:
                    dummy.extend(cluster)
            
            #Get status of processing mutants
            statusdict = {}
            statusdict["stage1"] = 0
            statusdict["stage2"] = 0
            statusdict["stage3"] = 0 #For future use
            statusdict["stage4"] = 0 #For future use
            statusdict["processing"] = 0
            statusdict["complete"] = 0
            statusdict['percentage'] = 0.00
            statusdict['estimated'] = ""

            #TODO: Support multistage projects.. this is just the status for             
            p = db.dbtable_mutants_status.find({"_id.id_project": idp}) #This is the view that gives us project status counters
            
            for stat in p:
               status = stat["_id"]["status"]
               cont   = stat["count"]
               
               if status == "pending":
                   statusdict["stage1"] = cont
                   
               elif status == "done":
                   statusdict["complete"]   = cont
                   statusdict["stage2"]     = cont
                   statusdict['percentage'] = round(100*(cont/int(mutants)),2)
                   
               elif status in ["processing"]:
                   statusdict["processing"] = cont
               else:
                   statusdict["in_process"] = cont
            
            #if there is an average already, get it
            #ask first..
            numberdocs = db.dbtable_mutants.count_documents({"id_project": idp, "status": {"$nin": ["pending","processing"]}, "status_vars.md_elapsed_time_seconds": {"$gt": 0}})
            #if there is data
            if numberdocs > 0:
                sumtime = 0
                timeCursor = db.dbtable_mutants.find( {"id_project": idp, "status": {"$nin": ["pending","processing"]}, "status_vars.md_elapsed_time_seconds": {"$gt": 0}}, {"_id": 0, "status_vars.md_elapsed_time_seconds": 1})
                for tim in timeCursor:
                    sumtime += int(tim["status_vars"]["md_elapsed_time_seconds"])
                avg = int(sumtime//numberdocs) #get avg seconds per run

                if statusdict["processing"] > 0: 
                   cardsinuse  = statusdict["processing"]; 
                   pendingtogo = str(display_time(avg*int(statusdict["stage1"]//cardsinuse),2))+" to go. (Average GPU-time per simulation: "+display_time(avg)+")"
                else: 
                   pendingtogo = "Scavenging Data..."

                statusdict['estimated'] = pendingtogo
            #if there is not
            else:
                if statusdict["complete"] > 0:
                    statusdict['estimated'] = "No status data was collected during run"
                elif int(statusdict["stage1"]) == int(mutants):
                    statusdict['estimated'] = "Waiting for project to start running!"
                else:
                    #Get the time remaining for the first "done" mutant to be available
                    timeCursor = db.dbtable_mutants.find({"id_project": idp, "status": "processing", "status_vars.md_elapsed_time_seconds": {"$gt": 0}}, {"_id": 0, "status_vars.md_remaining_time": 1, "status_vars.md_remaining_time_seconds": 1})
                    numberdocs = db.dbtable_mutants.count_documents({"id_project": idp, "status": "processing", "status_vars.md_elapsed_time_seconds": {"$gt": 0}})
                    prior = 10000000 #Something ridiculously high
                    text = ""
                    for tim in timeCursor:
                        sumtime = int(tim["status_vars"]["md_remaining_time_seconds"])
                        if sumtime < prior:
                            prior = sumtime
                            text  = "<br>("+str(numberdocs)+" running. Wait about "+tim["status_vars"]["md_remaining_time"]+" for first mutant)"
                            
                    statusdict['estimated'] = "Simulations started, collecting data! "+text
            
            #SInce 8 projects ran before being able to probe their status, this is necesary for the GUI
            if statusdict["percentage"] == 100:
                statusdict['estimated'] = "All scheduled simulations complete!"
                          
            anchors  = len(set(dummy))
            projs.append({'id': idp, 'name': name, 'date': date, 'mutants': mutants, 'clusters': clusters, 'anchors': anchors, 'status': statusdict})
            
    #print(projs)
    
    res = {
     "action": "render_projects",
     "component": "projectlist",
     "response": projs
    }
    
    return json.dumps(res)



# Delete a project
@app.route("/deleteProjectTree", methods=['GET', 'POST'])
def deleteProjectTree():
    try:
        #query for all projects
        data = json.loads(request.get_data())
        idp  = data['idproject']             
        
        #1-Get project folder
        pr     = db.dbtable_projects.find_one({"id_project": int(idp)},{"project_folder": 1})
        folder = pr["project_folder"]
        print(f"Identifying project folder {folder}")
        
        #2-Delete Project from projects table
        projects = db.dbtable_projects.delete_one({"id_project": int(idp)}) #PEDRO AUG 2024 - Add ordering by projectid
        mutants  = db.dbtable_mutants.delete_many({"id_project": int(idp)})
        scaveng  = db.dbtable_processed_data.delete_many({"id_project": int(idp)}) #Drop scavenged data
        
        deletedproj = str(projects.deleted_count)
        deletedmuts = str(mutants.deleted_count)
        deletedscavs = str(scaveng.deleted_count)
        print(f"Deleted {deletedproj} projects and {deletedmuts} mutants with {deletedscavs} scavenged data records")
        #3-Delete project directory Tree
        import shutil
        try:
         shutil.rmtree(folder)
        except Exception as e:
         print(f"Failed to delete project tree with: {e}")
            
        res = {
            "action": "delete_project",
            "component": "projectlist",
            "response": "Project Deleted!"
        }
    except:
        res = {
            "action": "delete_project",
            "component": "projectlist",
            "response": "Error deleting project"
        }
    return json.dumps(res)
   


#GET JOB CONTROL DATA TO SHOW IN THE WEB
@app.route("/getOngoingJobs", methods=['POST'])
def getOngoingJobs():

    data = json.loads(request.get_data())
    idp  = data['idproject']
    
    #
    project = list(db.dbtable_projects.find({'id_project': int(idp)}))
    name    = project[0]['project_name']
    path    = project[0]['project_folder']
    
    #
    num_mutants = db.dbtable_mutants.count_documents({'id_project': int(idp)}) #conut mutants in project
    allmutants  = list(db.dbtable_mutants.find({"id_project": int(idp)}, {"_id": 0, "id_project": 0, }))
    
    #PENDING EVERYTHING TO SHOW JOB CONTROL LIST




#GET ANCHOR POINTS FROM PROJECT
@app.route("/getAnchorPoints", methods=['POST'])
def getAnchorPoints():

    #query for all projects
    data = json.loads(request.get_data())
    idp  = data['idproject']                
    project = list(db.dbtable_projects.find({"id_project": idp}))

    dummy = list()
    for cluster in project[0]['clusters']:
        if cluster is not None:
            dummy.extend(cluster)
            
    anchors = set(dummy)
    
    res = {
     "action": "render_projects",
     "component": "projectlist",
     "response": anchors
    }
    
    return json.dumps(res)




#GET EXISTING PROJECT LIST FOR WEBSITE
@app.route("/getProjectData", methods=['POST'])
def getProjectData():
    
    data = json.loads(request.get_data())
    projectid = data['idproject']
    project = list(db.dbtable_projects.find({'id_project': int(projectid)}))
    
    res   = {}
    projs = []
        
    projs.append({'name': project[0]['project_name'], 'project_folder': project[0]['project_folder'] })
    
    #print(projs)
    res = {
     "action": "render_project",
     "component": "all",
     "response": projs
    }
    
    return json.dumps(res)


#GET ALL DATA FOR EXISTING PROJECT
@app.route("/getAllProjectData", methods=['POST'])
def getAllProjectData():
    
    data = json.loads(request.get_data())
    projectid = data['idproject']
    project = list(db.dbtable_projects.find({'id_project': int(projectid)},{'_id': 0}))
    
    res   = {}
    projs = []
    dummy = list()
    
    
    projs.append({'project': project[0]})
    
    print(projs)
    
    #print(projs)
    res = {
     "action": "fill_project_data",
     "component": "all",
     "response": projs
    }
    
    return json.dumps(res)





@app.route("/getMutantStatusTable", methods=['POST'])
def getMutantStatusTable():
    import copy
    
    #Fetch Projectid
    data = json.loads(request.get_data())
    projectid = data['idproject']
    
    # Query DB for mutants of the project, and exclude mutants/simulations which type is verification 
    mutants   = list(db.dbtable_mutants.find({"id_project": int(projectid), "status": "done", "type": { "$ne": "verification" } },{"_id": 0, "id_project": 0}))
    #Get validation/verification simulations in for this project, regardless of their status PEDRO AUG 2024
    replica   = list(db.dbtable_mutants.find({"id_project": int(projectid), "type": { "$eq": "verification" } },{"_id": 0, "id_project": 0}))
    
    processed = list(db.dbtable_mutants_ready.find({"id_project": int(projectid)}, {"_id": 0}))
    project   = list(db.dbtable_projects.find({"id_project": int(projectid)}, {"_id": 0, "clusters": 1, "residuemap": 1}))
    #TODO check if list is empty for whatever reason    
    deltas    = list(db.dbtable_mutants_deltag.find({"id_project": int(projectid)}, {"_id": 0, "deltag_total": 1}))
    deltas_df = pd.DataFrame(deltas)
    stats     = deltas_df.describe(percentiles=[0.001, 0.01, .05, .10, .20, .50, .80, .90])['deltag_total']
    #Basic stats array
    #Get basic statistics on delta series

    #Modify response to include replicas... that we use that dict for DataTables to display verification info on mutants that were validated in triplicate
    di = {"muts": mutants, "proc": processed, "proj": project, "descriptive": stats, "replicas": replica}
    
    res = {
        "action": "fillMutantTable_initial",
        "component": "mainModal",
        "response": di
    }
    
    return dumps(res)

#Returns project ResidueMap for CorrelationFinder
@app.route("/getResidueMap", methods=['POST'])
def getResidueMap():
    data = json.loads(request.get_data())
    projectid = data['idproject']
    project   = list(db.dbtable_projects.find({"id_project": int(projectid)}, {"_id": 0, "clusters": 1, "residuemap": 1}))

    di = {"proj": project}
    
    res = {
        "action": "residueMap",
        "component": "anchorpointlist",
        "response": di
    }
    
    return res
    

#BUILDS A COMPOUND WEBLOGO USING TOTAL ENERGY OF EACH MUTANT COMBINATION AS GUIDANCE. INCLUDES RELEVANCE OF EACH ANCHOR POINT
@app.route("/getMutantWebLogo", methods=['POST'])
def getMutantWebLogo():
    
    #Fetch Projectid
    data = json.loads(request.get_data())
    projectid = data['idproject']  
    #mutants    = list(db.dbtable_mutants.find({"id_project": int(projectid)},{"_id": 0, "id_project": 0}))
    
    processed  = list(db.dbtable_mutants_ready.find({"id_project": int(projectid)}, {"_id": 0}))
    #project    = list(db.dbtable_projects.find({"id_project": int(projectid)}, {"_id": 0, "clusters": 1, "residuemap": 1}))
    map        = db.dbtable_projects.find_one({"id_project": int(projectid)},{"residuemap": 1, "objects": 1})
    
    xlabel     = list() #Holds the X axis labels
    xmutables  = list()
    realpos    = list() #holds an array of the positions in the original PDB file
    wtseq      = list() #SEQ of wildtype anchorpoints, as they go in the weblogo
    dictseq    = {}
    anchordict = {}
    seqdata    = {'mutantID': []} # all mutated seqs in order
    dictanchors = {}
    #get mutable object
    for obje in map["objects"]:
        if obje["mutable"] == True:
            di = obje["chains"]
            chain = di[0]['key']

    for obj in map['residuemap']:
      for mut in map['residuemap'][obj]:
        if mut is not None:
            if mut["chain"] == chain:
                position_pdb = mut["resno_PDB"]
                position_ngl = mut["resno_NGL"]
                residue= mut["name"]
                if residue in res3to1:
                    rrr = residue
                    rr = res3to1[residue]
                    wtseq.append(rrr)
                    xlabel.append(rrr+str(position_pdb))
                    realpos.append(position_ngl)
                    dictseq[str(position_ngl)] = rrr
                    anchordict[str(position_ngl)]  = {"residue": rrr, "scores": {}, "position_label": rrr+str(position_pdb)}
                    seqdata[rrr+str(position_pdb)] = []
                    if mut["isanchor"] == True:
                      xmutables.append(rrr+str(position_pdb))
                      dictanchors[position_ngl] = f'{rr}{position_pdb}'
                else:
                    print("Skipping "+str(residue))

    seqdata['TotalEnergy'] = []

    #Weblogo
    energies   = [mutante['deltag_total'] for mutante in processed]
    mutations  = [mutante['mutations'] for mutante in processed]

    wt_energy = 0
    #Get WIldtype Energy
    for mut in processed:
        if mut['mutantID'] == 1:
            wt_energy = mut['deltag_total']

    #Build weblogo relevance dictionary
    #Create a dictionary with residues per anchorpoint, 
    #and accumulate the totalenergy of the mutant they appear in
    logdict = dict() 
    for m in range(0,len(energies)-1):
        if energies[m] < wt_energy and processed[m]['mutantID'] != 1:
            score = energies[m]
            mut   = mutations[m]
            if type(mut) == type(list()):
                for ele in mut:
                    mut = ele          
            for pos, residue in mut.items():
                pos = int(pos.split(':')[1])
                if pos not in logdict:
                    logdict[pos] = {}
                if residue not in logdict[pos]:
                    logdict[pos][residue] = 0
                if 'best' not in logdict[pos]:
                    logdict[pos]['best'] = 0
                logdict[pos][residue] += score
                if logdict[pos][residue] < logdict[pos]['best']:
                    logdict[pos]['best'] = logdict[pos][residue]
    
    #Prepare dictionary for weblogo logic
    #here I transform the
    try:
        bigger = [int(pos['best']) for pos in logdict.values()]#List comprenhend the min val of all anchors  
        bigger.sort()
        bigger = bigger[0]
    except:
        res = {
            "action": "renderWebLogo",
            "component": "weblogoGood_chart",
            "response": {}
        }
        return dumps(res)

    for pos, muts in logdict.items():
        print(type(muts))
        for res, score in muts.items():
            if res != 'best':
                perc = muts[res]/muts['best']
                logdict[pos][res] = round(perc,2)
        logdict[pos]['best'] = logdict[pos]['best']/bigger
        
    di = {"weblogo": logdict}
        
    res = {
            "action": "renderWebLogo",
            "component": "weblogoGood_chart",
            "response": di
    }
        
    return dumps(res)






@app.route("/getMutantRMSD", methods=['POST'])
def getMutantRMSD():
    data = json.loads(request.get_data())
    
    mutantID = data['mutantID']
    projectid = data['idproject']
    rmsd = list(db.dbtable_processed_data.find({"id_project": int(projectid), "mutantID": int(mutantID)}, {"_id": 0, "rmsd": 1}))
    
    di = {"mutantID": mutantID, "rmsd": rmsd[0]['rmsd']}
    
    res = {
        "action": "render_RMSD_graph",
        "component": "RMSD_chart",
        "response": di
    }
    
    return dumps(res)
    


@app.route("/getMutantWater", methods=['POST'])
def getMutantWater():
    data = json.loads(request.get_data())
    
    mutantID = data['mutantID']
    projectid = data['idproject']
    rmsd = list(db.dbtable_processed_data.find({"id_project": int(projectid), "mutantID": int(mutantID)}, {"_id": 0, "water_ids": 1}))
    
    di = {"mutantID": mutantID, "rmsd": rmsd[0]['rmsd']}
    
    res = {
        "action": "render_WATER_graph",
        "component": "WATER_chart",
        "response": di
    }
    
    return dumps(res)




@app.route("/getMutantEnergy", methods=['POST'])
def getMutantEnergy():
    data = json.loads(request.get_data())    
    mutantID = data['mutantID']
    projectid = data['idproject']
    
    #TODO check if list is empty for whatever reason
    energy = list(db.dbtable_mutants_deltag.find({"id_project": int(projectid), "mutantID": int(mutantID)}, {"_id": 0, "RES": 1, "LOC": 1,"TOT_ERR_PR": 1,"TOT_STD_PR": 1, "TOT_AVG_PR": 1, "mutations": 1, "cluster": 1, "combination": 1}))
    
    
    di = {"mutantID": mutantID, "energy": energy[0]}
    
    res = {
        "action": "render_ENERGY_graph",
        "component": "Energy_chart",
        "response": di
    }
    
    return dumps(res)
    


@app.route("/getPairwiseMap", methods=['POST'])
def getPairwiseMap():
    data = json.loads(request.get_data())
    mutantID = data['mutantID']
    projectid = data['idproject']
    
    #TODO check if list is empty for whatever reason
    pairwise = list(db.dbtable_mutants_deltag.find({"id_project": int(projectid), "mutantID": int(mutantID)}, {"_id": 0, "RES1": 1, "RES2": 1, "TOT_PW": 1, "mutations": 1, "cluster": 1}))
    
    di = {"mutantID": mutantID, "pairwise": pairwise[0]}
    
    res = {
        "action": "render_ENERGY_pairwise",
        "component": "Pairwise_chart",
        "response": di

    }
    
    return dumps(res)




@app.route("/getContactMap", methods=['POST'])
def getContactMap():
    
    import mdtraj as mt
    import MDAnalysis as md
    from MDAnalysis.coordinates.memory import MemoryReader
    from MDAnalysisTests.datafiles import PDB, XYZ
    
    data = json.loads(request.get_data())
    
    mutantID = data['mutantID']
    projectid = data['idproject']
    
    #Get trajectory file in H5 format    
    project = list(db.dbtable_projects.find({"id_project": int(projectid)}, {"_id": 0, "project_folder": 1}))
    folder  = project["project_folder"]
    path    = f'{folder}/mutants/{mutantID}/outputs/output_md.h5'
    
    #Get file
    traj  = mt.load_hdf5(path)
    nowat = traj.remove_solvent()
    top = StringIO(nowat.top)
    xyz = StringIO(nowat.xyz)
    
    
        
    di = {"mutantID": mutantID, "energy": energy[0]}
    
    res = {
        "action": "render_ENERGY_contactmap",
        "component": "Energy_contactmap_chart",
        "response": di
    }
    
    return dumps(res)




#Loads a PDB into memory and returns it to NGL Viewer
@app.route('/getBestMutantPose', methods=['POST'])
def getBestMutantPose():
    data = json.loads(request.get_data())
    mutantID  = data['mutantID']
    projectid = data['idproject']
    project = list(db.dbtable_projects.find({"id_project": int(projectid)}, {"_id": 0, "project_folder": 1}))    
    waters  = db.dbtable_processed_data.find_one({"id_project": int(projectid), "mutantID": int(mutantID)}, {"_id": 0, "water_ids": 1})
    
    folder  = project[0]["project_folder"]
    file    = "output_bestpdb.pdb"
    filewat = "output_bestpdb_wat.pdb" # For future use?
    path = f'{folder}/mutants/{mutantID}/outputs/'
    
    #Read PDB
    with open(path+file, 'r') as pdb:
        pdbtext = pdb.read()
    
    #Build response
    di = {"mutantID": mutantID, "pdbfile": pdbtext, "watersites": waters}
        
    
    res = {
        "action": "render_NGLmodel",
        "component": "#mutantviewer",
        "response": di
    }
    
    return dumps(res)


@app.route("/getAnchorStatusTable", methods=['POST'])
def getAnchorStatusTable():
    #Fetch Projectid
    data = json.loads(request.get_data())
    projectid = data['idproject']
    
    
    pass





################################################################################
## THIS CODE RESPONDS TO THE SPICIFICITY FINDER
################################################################################

#Returns a list of all projects with an equal scaffold or mutating ligand only
@app.route("/getProjectList", methods=['POST'])
def getProjectList():
    
    from Bio import SeqIO
    
      #Fetch Projectid
    data      = json.loads(request.get_data())
    targetproject = data['idproject']  
    
    project = list(db.dbtable_projects.find({}, {"_id": 0, "id_project": 1, "objects.chains.key": 1,"objects.mutable": 1, "residuemap": 1, "project_name": 1, "project_folder": 1}))
    
    #Extract sequence map of each project
    ali = {}
    ali["target"] = ""
    ali["compare"] = {}
    resultprojects = {}
    #Iterate every project in DYME - See which protein ligands match the actual project's (targetproject)
    for proj in project:
        obj = proj["objects"]
        idp = proj["id_project"]
        projfolder = proj["project_folder"]
        PDB_file_path = f'{projfolder}/inputs/original.pdb'
        for prop in obj:
            if prop['mutable'] == True:
                mutchain = prop["chains"][0]["key"]
        chain = {record.annotations['chain']: record.seq for record in SeqIO.parse(PDB_file_path, 'pdb-atom')} 
        seq = chain[mutchain]
        if int(idp) == int(targetproject):
            ali['target'] = seq
        else:
            ali['compare'][idp] = {}
            ali['compare'][idp]['seq']  = seq
            ali['compare'][idp]['name'] = proj["project_name"]
    #Build our resultset
    for seqid in ali['compare']:
        if ali['compare'][seqid]['seq'] == ali['target']:
            resultprojects[seqid] = {}
            resultprojects[seqid]['name'] = ali['compare'][seqid]['name']
            resultprojects[seqid]['seq']  = str(ali['compare'][seqid]['seq'])
        #for res in proj["residuemap"][mutchain]:
        #    if res != None:
        #        print(f'{idp}{res}')
        
    di = {"listelements": resultprojects}
    res = {
            "action": "renderDropdown",
            "component": "projectsdropdown",
            "response": di
    }
        
    return dumps(res)

#COmpare best 40 mutants of a project with another - must have the same protein ligand (or scaffold, or whatever mutable molecular object)
@app.route("/compareMutants", methods=['POST'])
def compareMutants():
    
    from Bio import SeqIO
    
    #Fetch Projectid
    data       = json.loads(request.get_data())
    target     = data['idorig']  
    compare_to = data['idcomp']  
    #Get mutants of both projects - 40 best from target - all available from the comparison
    mutants_targ = list(db.dbtable_mutants_ready.find({"id_project": int(target), "status": "done"}, {"_id": 0, "mutantID": 1, "deltag_total": 1, "mutations": 1, "combination": 1}).sort("deltag_total", 1).limit(40)) #Best 10 mutants of target - 20 from glori Feb 1 - 40 from Pedro oct 2024
    mutants_comp = list(db.dbtable_mutants_ready.find({"id_project": int(compare_to)}, {"_id": 0, "mutantID": 1, "deltag_total": 1, "mutations": 1, "combination": 1}))
    #Get project data (both)
    targetproj   = list(db.dbtable_projects.find({"id_project": int(target)}, {"_id": 0, "id_project": 1, "objects.chains.key": 1,"objects.mutable": 1, "residuemap": 1, "project_name": 1, "project_folder": 1}))[0] #Get target
    comparproj   = list(db.dbtable_projects.find({"id_project": int(compare_to)}, {"_id": 0, "id_project": 1, "objects.chains.key": 1,"objects.mutable": 1, "residuemap": 1, "project_name": 1, "project_folder": 1}))[0] #Get compare_to
    #Get wildtypes (energy of both)
    wt_target    = list(db.dbtable_mutants_ready.find({"id_project": int(target), "status": "done", "mutantID": 1}))[0]
    wt_compar    = list(db.dbtable_mutants_ready.find({"id_project": int(compare_to), "status": "done", "mutantID": 1}))[0]
    
    
    #Check that all values are ready for returning the table
    if (len(mutants_targ) == 0) or (len(mutants_comp) == 0):
        print(mutants_targ)
        #print(mutants_comp)
        
        di = {"error": "The project you selected doesn't have any mutants. Please wait for some of its simulations to finish, and try again"}
        res = {
                "action": "renderError",
                "component": "wizzardModal",
                "response": di
        }
        return dumps(res)   
    #print(targetproj)
    #Get Mutable Chain of Target
    for prop in targetproj['objects']:
        if prop['mutable'] == True:
           mutchain_target = prop["chains"][0]["key"]
    
    for prop in comparproj['objects']:
        if prop['mutable'] == True:
           mutchain_compar = prop["chains"][0]["key"]
    
    #Get starting positions of same protein ligand in both projects (from the PDB, and chains sotred in the DB)
    target_start = {record.annotations['chain']: f"{record.annotations['start']} - {record.annotations['end']}" for record in SeqIO.parse(targetproj['project_folder']+'/inputs/original.pdb', 'pdb-atom')}
    compar_start = {record.annotations['chain']: f"{record.annotations['start']} - {record.annotations['end']}" for record in SeqIO.parse(comparproj['project_folder']+'/inputs/original.pdb', 'pdb-atom')}
    init,  end   = target_start[mutchain_target].split(" - ")
    initc, endc  = compar_start[mutchain_compar].split(" - ")
    ##---------------
    map = {}
    #Build mapt from Target to Compar
    for pos in range(int(init), int(end)+1):
        index = f"{mutchain_target}:{pos}"
        map[index] = f"{mutchain_compar}:{initc}"
        initc = int(initc)+1
    
    #mapped = []
    matches = {}
    matches['target_name'] = targetproj['project_name']
    matches['compar_name'] = comparproj['project_name']
    matches['target_wt_energy'] = wt_target['deltag_total'] 
    matches['compar_wt_energy'] = wt_compar['deltag_total'] 
    
    for mut in mutants_targ:
        m = mut['mutations']
        if type(m) is list:
            m = m[0]
        mid = mut['mutantID']
        mdelta = mut['deltag_total']
        combi_target = mut['combination']
        ins = {}
        for key in m:
          translated = map[key]
          ins[translated] = m[key]
          #mapped.append(ins) #Store translated? nahh let's do the loop here
        for compare in mutants_comp:
            c = compare['mutations']
            if type(c) is list:
                if len(c) > 0:
                    c = c[0]
            if ins == c: #If both dictionaries have the same indexes and values - we have a match between project tarjet and compar
                cid    = compare['mutantID']
                cdelta = compare['deltag_total']
                combi_compar = mut['combination']
                matches[mid] = {}
                matches[mid]['target_id_mutant'] = f"{mid} ({combi_target})"
                matches[mid]['target_mutations'] = m
                matches[mid]['target_energy']    = mdelta
                matches[mid]['compar_energy']    = cdelta
                matches[mid]['compar_mutations'] = c
                matches[mid]['compar_id_mutant'] = f"{cid} ({combi_compar})"
                matches[mid]['difference']       = mdelta-cdelta
                
    #Compose Response vector
    di =  {"matrix": matches, 'residuemap_target': targetproj['residuemap'], 'residuemap_compar': comparproj['residuemap']}
    
    res = {
            "action": "renderMatchTable",
            "component": "projectmatchtable",
            "response": di
    }
        
    return dumps(res)


#Retrieve the wetspots of a mutant.
@app.route("/getWetspots", methods=['POST'])
def getWetspots():
    
    #A little private function to detect consecutive numbers in a list
    def group_consecutives(vals, step=1):
        """Return list of consecutive lists of numbers from vals (number list)."""
        run = []
        result = [run]
        expect = None
        for v in vals:
            if (v == expect) or (expect is None):
                run.append(v)
            else:
                run = [v]
                result.append(run)
            expect = v + step
        return result
    
    #Decimate array elements
    def GetSpacedElements(array, numElems = 10):
        out = array[np.round(np.linspace(0, len(array)-1, numElems)).astype(int)]
        return out.tolist()
          
    
    data = json.loads(request.get_data())
    mutantID  = data['mutantID']
    projectid = data['idproject']
    
    #Load project path and water info from mutant
    project    = list(db.dbtable_projects.find({"id_project": int(projectid)}, {"_id": 0, "project_folder": 1}))[0]
    water_info = list(db.dbtable_processed_data.find({"id_project": int(projectid), "mutantID": int(mutantID)}, {"_id": 0, "water_ids": 1}))[0]
    #Get path to MD
    path     = project['project_folder']+"/mutants/"+str(mutantID)+"/outputs/output_md.h5"
    pathsave = project['project_folder']+"/mutants/"+str(mutantID)+"/outputs/"
    
    import mdtraj as md
    import numpy
    
    #make a list with important waters
    if len(water_info["water_ids"]["important_waters"]) > 0:
        #The mutant has important waters in the interface
        important_waters = []
        for atomid in water_info["water_ids"]["important_waters"]:
            important_waters.append(atomid)
    else:
        #The mutant has no important waters in the interface
        res = {
                "action": "returnWetspots",
                "component": "wetspotTable",
                "response": []
        }
        return res
    
    
    #load trajectory   
    traj = md.load(path)
    traj = traj.image_molecules() #Recenter and apply periodic boundary conditions to the molecules in each frame of the trajectory.
    
    frame_combos = []
    #Put this in a LOOP for each water atom
    for atom in important_waters:
        coords = traj.xyz[:,int(atom)] #get all xyz positions from all frames for atomid
        
        #Find this water's distance from every frame to its next frame - in angstroms
        frames = []
        for i in range(0,len(traj.xyz)-1):
            dist = numpy.linalg.norm(coords[i]-coords[i+1])*10
            if dist < 3:
                frames.append(i) #list of frames where displacement was less than 3 angstroms
            
        #Find longest consecutive frame transitions where water was not moving
        grouped = group_consecutives(frames) #find arrays of consecutive numbers
        most_consecutive = grouped.index(max(grouped, key=len)) #find the longest consecutive set of frames
        most_consecutive_frames = grouped[most_consecutive]
        frame_combos.append(most_consecutive_frames)
        
        #get the biggest set of consecutive frames where this water seems to be moving slow
        #= traj.xyz[most_consecutive_frames, int(atom)]

    #BUILD WET SPOT VIEWER
    # WE TAKE THE CARTESIAN POINT OF ALL CONTINUOUS FRAME OF EACH WATER
    # AND WE BUILD A GRADIENT/MESH WITH IT



    #CREATE VIEW FOR NGL TRAJECTORY - ONLY IMPORTANT WATERS AND PROTEIN
    #WE TAKE 10 FRAME SAMPLES FROM EVERY WATER ATOM AND BUILD A SMALLER TRAJ
    
    #Select all protein atoms
    simplified = traj.top.select("protein")
    #Add important_water atomids to selection
    for wat in important_waters:
        simplified = np.append(simplified, int(wat))
        
    #Decimate trajectory with only protein and important water atoms
    decimated = traj.atom_slice(simplified)
    
    #Get 10 evenly spaced frames from each frame_combo
    concatenated = []
    for combo in frame_combos:
        #TODO: Check if there are more than 10 items and deliver the right numbeer of frames
        concatenated.extend(GetSpacedElements(np.array(combo),10)) #get 10 even frames from every combo
    concatenated.sort() #sort frames in order
    relevant = list(set(concatenated)) #remove duplicate frames
    
    #create special trajectory from decimated
    decimated = decimated[relevant]
    decimated.superpose(decimated,0)
    #save special trajectory for wetspots
    decimated.save_xtc(pathsave+"water_traj.xtc") #water trajectory in xtc compressed format
    decimated[0].save_pdb(pathsave+"water_topo.pdb") #topology (needed by NGLviewer)

    response = {"path_trajectory": f"img/projects/{projectid}/mutants/{mutantID}/outputs/water_traj.xtc",
                "path_topology":   f"img/projects/{projectid}/mutants/{mutantID}/outputs/water_topo.pdb"
               }

    #The mutant has no important waters in the interface
    res = {
           "action": "build_wetspots",
           "component": "showWetSpots",
           "response": response
          }
    return res
    


#Retrieve the wetspots of a mutant.
@app.route("/getHbondTable", methods=['POST'])
def getHbondTable():
    data      = json.loads(request.get_data())
    projectid = data['idproject']
    mutantID  = data['mutantID']
    
    
    project    = list(db.dbtable_projects.find({"id_project": int(projectid)}))
    map        = project[0]['residuemap']
    objs       = project[0]['objects']
    path       = project[0]['project_folder']
    mutantdir  = f"{path}/mutants/{mutantID}"
    prmtop     = f"{mutantdir}/inputs/receptor_ligand_wat.prmtop"
    trajectory_h5 = f"{mutantdir}/outputs/output_md.h5"
    trajectory_nc = f"{mutantdir}/outputs/output_md.nc"
    
        
    #Get which object is which
    for prop in objs:
        if prop['mutable'] == True:
           mutchain_target = prop["chains"][0]["key"]
    
    #SPLIT MOLECULAR OBJECTS IN TWO (receptor / ligand) ARRAYS
    dict_receptor = {}
    dict_ligand   = {}
    
    ligmask = []
    recmask = []
    
    ###################END VDW ANALYSIS##############
    #YOU DECIDED TO SCAVENGE ALL CPPTRAJ ATOMS DIRECTLY INTO THE DATABASE, THE CODE ABOVE NEEDS TO BE ADDED TO THE SCAVENGER NODE
    #TODO: MOVE CODE TO SCAVENGER AFTER HBONDS
    total_atoms = 0
    backbone_atoms = 0
    base_sidechain_atoms = 0
    dict_ligand = []
    cpptraj1     = list(db.dbtable_processed_data.find({"id_project": int(projectid), "mutantID": mutantID}, {"cpptraj_forward": 1, "cpptraj_reverse": 1,"cpptraj_forward20": 1, "cpptraj_reverse20": 1,"cpptraj_forward50": 1, "cpptraj_reverse50": 1, "_id": 0}))
    map          = list(db.dbtable_projects.find({"id_project": int(projectid)}, {"residuemap": 1}))[0]
    
    #GET ANchorpoints to highlight in red
    anchors = []
    for obj in map['residuemap']:
          for mut in map['residuemap'][obj]:
            if mut is not None:
             if mut["isanchor"] == True:
                #position_pdb = mut["resno_PDB"]
                position_ngl = mut["resno_NGL"]
                residue      = mut["name"]
                ngl_map      = f"{residue}{position_ngl}"
                anchors.append(ngl_map)
                
    #Return CPPTRAJ contacts to website            
    if len(cpptraj1) > 0:
        cf = cpptraj1[0]["cpptraj_forward"]
        cr = cpptraj1[0]["cpptraj_reverse"]
        cf20 = cpptraj1[0]["cpptraj_forward20"]
        cr20 = cpptraj1[0]["cpptraj_reverse20"]
        cf50 = cpptraj1[0]["cpptraj_forward50"]
        cr50 = cpptraj1[0]["cpptraj_reverse50"]
    else:
        cf = []
        cr = []
        cf20 = []
        cr20 = []
        cf50 = []
        cr50 = []
        

    nam = f"mut_{mutantID}"

    #################################################
    response = {"mutantID": mutantID, "hbonds": dict_ligand, "counters": {"total": total_atoms, "backbone": backbone_atoms, "side": base_sidechain_atoms}, "anchors": anchors, "cpptraj_forward": cf, "cpptraj_reverse": cr,"cpptraj_forward20": cf20, "cpptraj_reverse20": cr20,"cpptraj_forward50": cf50, "cpptraj_reverse50": cr50, 'name': nam}
    ##################################################    
    res = {
           "action": "render_hbonds_table",
           "component": "hbondsTable",
           "response": response
    }
    
    return res






#Enqueue verifications in triplicate for a mutantID of a project. - PEDRO AUG 2024
@app.route("/verifyInTriplicate", methods=['POST'])
def verifyInTriplicate():
    data      = json.loads(request.get_data())
    projectid = data['idproject']
    mutantID  = data['mutantid']
    
    #Check if the mutantID has not been verified in triplicate
    hastriplicates = db.dbtable_mutants.count_documents({"id_project": int(projectid), "parentID": int(mutantID)})
    if hastriplicates > 0:
        res = {
            "action": "returnTriplicateQueue",
            "component": "",
            "response": "This mutant is already verified"
        }
        
        print("Mutant " + str(mutantID) + " already validated in triplicate, exiting")
        return res
    
    
    #Query
    mutant      = db.dbtable_mutants.find_one({"id_project": int(projectid), "mutantID": int(mutantID)})
    maxid       = db.dbtable_mutants.find_one({"id_project": int(projectid)}, sort=[("mutantID", -1)])
    mut         = []
    
    newmut1 = {
              "id_project": int(projectid), 
              "status": 'pending', 
              "mutantID": int(maxid["mutantID"])+1, 
              "mutant": mutant["mutant"], 
              "parentID": int(mutantID),
              "combination": mutant["combination"], 
              "cluster": mutant["cluster"], 
              "type": "verification"
    }
    
    newmut2 = {
              "id_project": int(projectid), 
              "status": 'pending', 
              "mutantID": int(maxid["mutantID"])+2, 
              "mutant": mutant["mutant"], 
              "parentID": int(mutantID),
              "combination": mutant["combination"], 
              "cluster": mutant["cluster"], 
              "type": "verification"
    }
    
    #Create mutant list
    mut.append(newmut1)
    mut.append(newmut2)
    
    #Exec query
    db.dbtable_mutants.insert_many(mut)
    print("Inserted 2 instances of mutant " + str(mutantID) + " for validation")
    #Return to GUI
    res = {
            "action": "returnTriplicateQueue",
            "component": "",
            "response": "Success!. 2 more replicas have been queued for simulation"
    }
    
    return res




#Simulate the same mutant more times
@app.route("/simulateAgain", methods=['POST'])
def simulateAgain():
    data      = json.loads(request.get_data())
    projectid = data['idproject']
    mutantID  = data['mutantid']
    howmany   = int(data['iterations'])
    
    #Query
    mutant      = db.dbtable_mutants.find_one({"id_project": int(projectid), "mutantID": int(mutantID)})
    maxid       = db.dbtable_mutants.find_one({"id_project": int(projectid)}, sort=[("mutantID", -1)])
    mut         = []
    
    cmaxid = int(maxid["mutantID"]) #Get current max id of the project in the mutants table
    
    for currentmax in range(cmaxid+1, cmaxid+howmany+1):
        newmut = {
                "id_project": int(projectid), 
                "status": 'pending',
                "mutantID": currentmax,
                "mutant": mutant["mutant"], 
                "parentID": int(mutantID),
                "combination": mutant["combination"], 
                "cluster": mutant["cluster"], 
                "type": "verification"
        }
  
        #Create mutant list
        mut.append(newmut)
    
    #Exec query
    db.dbtable_mutants.insert_many(mut)
    print("Inserted "+str(howmany)+" instances of mutant " + str(mutantID) + " for simulation")
    
    #Return to GUI
    res = {
            "action": "returnSimulateAgain",
            "component": "",
            "response": f"Success!. {howmany} more replicas have been queued for simulation"
    }
    
    return res



#TEST VDW ANALYSIS IN CRE RECOMBINASE WITH GLORIAS TRAJECTORIES
@app.route("/getGloriTable", methods=['POST'])
def getGloriTable():
    data      = json.loads(request.get_data())
    projectid = data['idproject']
    mutantID  = data['mutantID']

    #Get list of trajectory paths and prmtops
    '''
    pathgloriafiles = "/superfast2/dyme/projects/gloria/Cre_wt_Langevin_SPCE_a20_ff14SB_150mM/"
    trajectory_nc = "/receptor_ligand_md7_reimagined_noWAT.mdcrd"
    prmtop = "/receptor_ligand.prmtop"
    
    dict_receptor = {} ## Receptor dictionary-- Fill manually
    dict_ligand   = {} ## Ligand Dictionary-- Fill manually    
        
    
    print("Loading PRMTOP")
    print("Loading "+pathgloriafiles+prmtop)
    top = md.Universe(pathgloriafiles+prmtop)
    for ts in top.residues:
        ngl = str(ts.resname)+str(ts.resnum)
        if int(ts.resnum) < 645:
            dict_ligand[ngl] = {}
        else:
            dict_receptor[ngl] = {}
    print("BUILT dictionaries of lig rec")
    '''
    ###################END VDW ANALYSIS##############
    #YOU DECIDED TO SCAVENGE ALL CPPTRAJ ATOMS DIRECTLY INTO THE DATABASE, THE CODE ABOVE NEEDS TO BE ADDED TO THE SCAVENGER NODE
    #TODO: MOVE CODE TO SCAVENGER AFTER HBONDS
    total_atoms = 0
    backbone_atoms = 0
    base_sidechain_atoms = 0
    dict_ligand = []
    cpptraj1     = list(db.dbtable_mutants_gloria.find({"id_project": 100}, {"cpptraj": 1, "cpptraj_reverse": 1, "cpptraj_dna_dna": 1, "name": 1, "_id": 0}))
    #print(cpptraj1)            
   
    #################################################
    response = {"mutants": cpptraj1}
    ##################################################    
    res = {
           "action": "render_hbonds_table",
           "component": "hbondsTable",
           "response": response
    }
    
    return res



#Mark mutant for refinement (tag/untag)
@app.route("/toggleTagMutant", methods=['POST'])
def toggleTagMutant():
    
    data      = json.loads(request.get_data())
    projectid = data['idproject']
    mutid     = data['mutantid']
    
    #Get data from single mutant in single project
    mutant_data = db.dbtable_mutants.find_one({"id_project": int(projectid), "mutantID": int(mutid)})
    print(mutant_data)
    print(f"{projectid} and {mutid}")
    #Solve whether this mutant has been tagged before
    if "tagged" in mutant_data:
        print("tagged attribute exists in mutant, toggling")
        #If so.. get the curent tag status
        status = mutant_data["tagged"]
        if status == "yes":
           db.dbtable_mutants.update_one({"id_project": int(projectid), "mutantID": int(mutid)}, {"$set": {"tagged": "no"}})
        else:
           db.dbtable_mutants.update_one({"id_project": int(projectid), "mutantID": int(mutid)}, {"$set": {"tagged": "yes"}})
    else:
        #If not, set the flag in "yes" to start with... tag will be updated to "no" if the mutant is untagged
        print("tagged attribute doesn't exist")
        db.dbtable_mutants.update_one({"id_project": int(projectid), "mutantID": int(mutid)}, {"$set": {"tagged": "yes"}})
               
    mutants = {}
    #Default response
    res = {
           "action": "toggle_tag",
           "component": "datatablesjobs",
           "response": mutants
          }
    return res
    




    
#Get Job List
@app.route("/getProjectJobs", methods=['POST'])
def getProjectJobs():

    data      = json.loads(request.get_data())
    projectid = data['idproject']    
    print(projectid)
    mutants   = list(db.dbtable_mutants.find({"id_project": int(projectid)}, {"_id": 0, "id_project": 0}))
    
    #The mutant has no important waters in the interface
    res = {
           "action": "render_jobs_table",
           "component": "datatablesjobs",
           "response": mutants
          }
    return res


#Generate DYME-VMD launcher button
#1. Generate NC trajectory for mutant
#2. Create vmdload.vnc template with paths
#3. Return to site and launch xdg-open

@app.route("/launchVMD", methods=['POST'])
def launchVMD():
    from subprocess import run, call, Popen, PIPE
    
    data      = json.loads(request.get_data())
    projectid = data['idproject']
    mutantID  = data['mutantID']
        
    project    = list(db.dbtable_projects.find({"id_project": int(projectid)}))
    path       = project[0]['project_folder']
    mutantdir  = f"{path}/mutants/{mutantID}"
    
    #Define files
    trajectory_h5 = f"{mutantdir}/outputs/output_md.h5"
    trajectory_nc = f"{mutantdir}/outputs/output_md.nc"
    prmtop        = f"{mutantdir}/inputs/receptor_ligand_wat.prmtop"
    loader        = f"{mutantdir}/outputs/vmdload.vmd"
    
    #1.Generate NC trajectory
    #if not os.path.isfile(trajectory_nc):
    #Doesn't exist. Create it
    #TODO: Make mdconvert path come from settings
    #consider doing this with mdtraj/pytraj ... we have to image the molecules to center
    if os.path.isfile(trajectory_nc): 
       os.remove(trajectory_nc)
        
    import mdtraj as md
    print('Creating NC format from the original HDF5 trajectory in Project Dir!')
    print(trajectory_h5)
    traj = md.load(trajectory_h5)
    print('Imaging molecules')
    traj.image_molecules(inplace=True)
    # 2. Center coordinates (move system to origin, solvent included)
    traj.center_coordinates()
    # 3. Align entire system to the first frame (solvent + protein)
    traj.superpose(traj, frame=0)        

    print('Saving a NetCFD copy of the file')
    traj.save_netcdf(trajectory_nc)
    traj = None
    #BETTER WITH MDTRAJ...
    print('NC Trajectory created!')

    #2. Create vmdload.vmd
    vmd = vmdLoader(trajectory_nc, prmtop, loader, projectid, mutantID)
    
    #3. Return to site and launch xdg-open
    #TODO: Make VMD path come from settings
    link = f"app:///group/bioinfp_apps/vmd/bin/vmd -e {loader}"

    with open(loader, "r", encoding="utf-8") as f:
     content = f.read()
    
    #The mutant has no important waters in the interface
    res = {
           "action": "launch_vmd_external",
           "component": "loadingVMDmodal",
           "response": link,
           "content": content,
           "mutantidvmd": mutantID
          }
    
    return res



#Get a combination of anchor points with aminos, return all ids that match. Separated by comas
@app.route("/getFilterTable", methods=['POST'])
def getFilterTable():
    
    data      = json.loads(request.get_data())
    projectid = data['idproject']
    criteria  = data['criteria']
    
    print(criteria)
    #Get ids that match the filter from mutants table
    mutants   = list(db.dbtable_mutants.find({"id_project": int(projectid), "status": "done"}, {"_id": 0, "id_project": 0, "status": 0, "combination": 0, "type": 0, "status_vars": 0, "cluster": 0}))

    filterids = [1]
    
    for mutant in mutants:
        combination = mutant["mutant"] #get all mutations from this mutant
        
        #FOR SINGLETS
        if len(criteria) == 1:
            #print("Probing for Singlets")
            ind  = criteria[0]["index"]
            crit = criteria[0]["res"]
            if ind in combination:
                if combination[ind] == crit:
                    filterids.append(int(mutant["mutantID"]))
        #FOR DUPLETS                    
        if len(criteria) == 2:
            #print("Probing for Duplets")
            ind1  = criteria[0]["index"]
            crit1 = criteria[0]["res"]
            ind2  = criteria[1]["index"]
            crit2 = criteria[1]["res"]            
            if (ind1 in combination) and (ind2 in combination):
                if combination[ind1] == crit1 and combination[ind2] == crit2:
                    filterids.append(int(mutant["mutantID"]))
         
        #FOR TRIPLETS
        if len(criteria) == 3:
            #print("Probing for Triplets")
            ind1  = criteria[0]["index"]
            crit1 = criteria[0]["res"]
            ind2  = criteria[1]["index"]
            crit2 = criteria[1]["res"]            
            ind3  = criteria[2]["index"]
            crit3 = criteria[2]["res"]  
            if (ind1 in combination) and (ind2 in combination) and (ind3 in combination):
                if combination[ind1] == crit1 and combination[ind2] == crit2 and combination[ind3] == crit3:
                    filterids.append(int(mutant["mutantID"]))
                    
        # For any of the selected (not exclusive)
        #for crit in criteria: #for each criteria we are using
        #    #print(f"Looking for {crit['index']}: {crit['res']} in {combination}")
        #    ind = crit["index"]
        #    if ind in combination:
        #        if combination[ind] == crit["res"]:
        #            print(f"Found {combination[ind]}")
        #            print(f'Adding {mutant["mutantID"]}')
        #            filterids.append(int(mutant["mutantID"]))
        
    
    res = {
           "action": "filter_table",
           "component": "datatable2",
           "response": filterids
          }
    
    return res



@app.route("/addMutantFromFilter", methods=['POST'])
def addMutantFromFilter():
    
    data      = json.loads(request.get_data())
    projectid = data['idproject']
    criteria  = data['criteria']
    
    #print(criteria)
    
    maxid       = db.dbtable_mutants.find_one({"id_project": int(projectid)}, sort=[("mutantID", -1)])
    #Get next id
    cmaxid = int(maxid["mutantID"])+1 #Get current max id of the last mutant

    mutant      = {}    
    #build mutant
    for x in criteria:
        ind = x["index"]
        re  = x["res"]
        mutant[ind] = re
    
    print(f'Inserting mutant {mutant} into mutant table')
    newmut = {
                "id_project": int(projectid), 
                "status": 'pending',
                "mutantID": cmaxid,
                "mutant": mutant, 
                "combination": "manual", 
                "cluster": "0", 
                "type": "user_defined"
    }
  
    #Exec query
    print(newmut)
    db.dbtable_mutants.insert_one(newmut)
           
    res = {
           "action": "queued_simulation",
           "component": "datatable2",
           "response": str(cmaxid)
          }
    
    return res



"""
#CALLS to get return jsons
#SYSTEM FUNCTIONS
@app.get("/doLogin")
def doLogin():
    session["username"] = ""
    session["iduser"] = ""
    
    #Read
    data = json.loads(request.args.post('userdata'))
    element = data['element']
    
    #Reply
    res = {
        "action": "",
        "component": "",
        "response": ""
        }
       
    return json.dumps(res)

#DYME FUNCTIONS
@app.get("/")
def hello():
    if "count" in session:
        session["count"] +=22
        if request.args.get('action') == "reset":
              session["count"] = 0
        
    return str(session["count"])

"""
    
#MAIN FLASK APP LAUNCH
if __name__ == "__main__":
    app.run()
