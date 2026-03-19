# -*- coding: utf-8 -*-
"""
DYME - Dynamic Mutagenesis Engine v0.1

File:           MainNode.py
Description:    Main Node Class

Purpose:        -Provides Orchestration & Pipeline coordination Methods

Provides:       -class MainNode()

Author:     
Pedro Manuel Guillem Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>
Structural Bioinformatics Laboratory - BIOTEC - Pisabarro Group
Technische Universität Dresden
Feb 2023
"""

import uuid
import time
from threading import Thread
from dyme import Node

class MainNode(Node.Node, Thread):
        
    #Constructor for MainNode
    #-------------------------------------------------------------------------
    def __init__(self, dyme):
        super(MainNode, self).__init__()
        self.node_type = "Main" #This Node Type
        self.queue_name = "all" #Queues to suscribe to
        
        self.instance_id = uuid.uuid4().hex
        self.dyme_core = dyme
        self.datetime_start= time.time()
        self.status = "initializing"
        
        #Internal pool of nodes
        self.nodepool = {}
                
        
        
        print("Booting Main Node")
        return    
    
    
    
    #Thread Start() override
    def run(self):
        #Connect to Database
        print("Connecting NoSQL Database")
        self.connectDatabase()
        
        #Connect to Database
        print("Connecting to Queue Broker")
        self.eventConnectAMPQ(self.dyme_core)
        
        #Run forever
        while(True):
            time.sleep(0.3)
            
            #do some checks to see stuf
        
        
    #Constructor post init
    #-------------------------------------------------------------------------
    def __post_init__(self):
        #self.full_name = self.first_name + " " + self.last_name
        return   
    #-------------------------------------------------------------------------
        
    
    
    
    
    
    #MainNode Specific Control Functions
    #-------------------------------------------------------------------------
    def launchNode(self, nodeType, launchMethod, host, launchArgs):
        return

    def pollNode(self):
        return 

    def killNode(self):
        return       
    
    #Knock-knock on all nodes
    def discoverNeighborhood(self):
        return

    #Update the list of online servers in the LAN
    def updateServerList(self):
        return

    #Kill all remote worker nodes        
    def destroyAllNodes(self):
        return
    
    #Pause all workers from doing whatever they are doing
    def pauseAllNodes(self):
        return
    
    #Resume work on all nodes
    def resumeAllNodes(self):
        return
    
    #Pause one node
    def pauseOneNode(self):
        return
    
    #Resume One Node
    def resumeOne(self):
                  return
    
    #Report status of all nodes to the GUI
    def retrieveAndBuildReport(self):
        pass
    
    #-------------------------------------------------------------------------
    
    
    
    
    #Action Processor
    def msgProcess(self, msg, args=""):
        #Here the code to process incoming messages
        match msg:
            case 400:
            return "Bad request"
            case 404:
            return "Not found"
            case 418:
            return "I'm a teapot"
            # If an exact match is not confirmed, this last case will be used if provided
            case _:
            return "Something's wrong with the internet"   
        