# -*- coding: utf-8 -*-
"""
DYME - Dynamic Mutagenesis Engine v0.1

File:           DymeDB.py
Description:    Database Access Functions

Purpose:        -Provides Database Access Routines

Provides:       -class DymeDB()

Author:     
Pedro Manuel Guillem Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>
Structural Bioinformatics Laboratory - BIOTEC - Pisabarro Group
Technische Universität Dresden
Feb 2023
"""

import sys
import os
import threading
import pymongo as db
import ssl
import pika as rabbit
import configparser as cp
import multiprocessing as mp
import psutil as ps
from os.path import exists


class DymeDB:
        
    def __init__(self, host=""):        
        #Internal pool of nodes
        print("Communicating with database")
         #DYME RUNTIME VARIABLES 
        self.script_dir   = self.get_script_dir()
        self.configfile   = os.path.join(self.script_dir, "config.ini")
        self.status       =   "initializing"
    
        self.loadconfig(str(host))
        self.connectDatabase()

    def get_script_dir(self):   
        if getattr(sys, 'frozen', False):
            # The app is running in a stabdalone executable bundle
            return os.path.dirname(sys.executable)
        else:
            # Normal Python environment
            return os.path.dirname(os.path.abspath(__file__))
    
    def disconnectDatabase(self):
        print()
        print("Disconnecting Database.. Ok")
        self.dbclient.close()
        
    def __exit__(self):
        print("Closing Database conn")
        self.disconnectDatabase()

    #Load Config File (dyme.cfg)
    def loadconfig(self, hostname=""):
        #IF USER DIDN'T PROVIDE A HOST OR IP ADDRESS
        if(hostname == ""):        
            config = cp.ConfigParser()
            config.sections()
                        
            if exists(self.configfile):
                config.read(self.configfile)
                print("Loaded config file")
            else:
                raise ValueError('ERROR: Config file not found '+self.configfile)
            #Assign local config to class vars
            self.dbhost = config["DB"]["hostname"]
            self.dbport = config["DB"]["port"]
        else:
            self.dbhost = str(hostname)
            self.dbport = str(27017)
            print("Using provided hostname or IP: "+str(hostname))
        self.CONNECTION_MONGO = "mongodb://"+self.dbhost+":"+self.dbport+"/dyme?retryWrites=true&connectTimeoutMS=600000&ssl=false"        
        print("")
            
    
    #DATABASE FUNCTIONS
    #Open Database Connection
    def connectDatabase(self):
        #Hook Database
        print("Connecting Database at: "+self.dbhost)
        try:
             conn = db.MongoClient(self.CONNECTION_MONGO)
             self.dbclient = conn.get_database()

        except db.errors.ConnectionFailure as e:
             raise ValueError("ERROR: Could not connect to Dyme Database:" + e)

        print("Database Connected Successfully!")
        #Map Collections to Variables
        #self.dbtable_system    = self.dbclient["system"]
        self.dbtable_mutants   = self.dbclient["mutants"]
        self.dbtable_projects  = self.dbclient["projects"]
        self.dbtable_frames    = self.dbclient["frames"]
        #self.dbtable_mindsdb   = self.dbclient["mindsdb"]
        self.dbtable_default_settings = self.dbclient["default_settings"]
        self.dbtable_processed_data = self.dbclient["processed_data"]
        self.dbtable_mutants_deltag = self.dbclient["mutants_deltag"]
        self.dbtable_mutants_ready  = self.dbclient["mutants_ready"]
        self.dbtable_mutants_status = self.dbclient["mutants_status"]
        #self.dbtable_mutants_gloria = self.dbclient["mutants_gloria"]
        
        self.status = "running"
        
        print("MongoDB connected OK")
        print("")

    #Disconnect Client
    def getcollection(self, table):
        return self.dbclient[table]

    def insert_document(self, table, doc_dict):
        collection = self.dbclient[table]
        result = collection.insert_one(doc_dict)
        print("Inserting record")
        return result.inserted_id

    def select_document(self, table, query_dict):
        collection = self.dbclient[table]
        result = collection.find_one(query_dict)
        print("Selecting record")
        if result is not None:
            return result
        else:
            return {}

    def update_document(self, table, query_dict, update_dict):
        collection = self.dbclient[table]
        result = collection.update_one(query_dict, {'$set': update_dict})
        print("Updating record")
        return result.modified_count
    
    
