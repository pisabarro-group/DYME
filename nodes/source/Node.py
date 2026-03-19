# -*- coding: utf-8 -*-
"""
DYME - Dynamic Mutagenesis Engine v0.1

File:           Node.py
Description:    Prototype for all Node Types

Purpose:        -Provides skeleton and common Node operations

Provides:       -class Node()

Author:     
Pedro Manuel Guillem Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>
Structural Bioinformatics Laboratory - BIOTEC - Pisabarro Group
Technische Universität Dresden

Nov 2023 - Added Prototypes for DB connection 
           Added AMPQ queue manager connection


"""

import sys
import os

import ssl
import pika as rabbit
import multiprocessing as mp
import psutil as ps

#Our own
from DymeDB import DymeDB

class Node:
    
    #Node vars
    instance_id = 0   #Unique node ID in the swarm
    datetime_start  = 0    #Date of creation
    log         = []    #Log list
    node_type   = ""    #type of Node
    lictoken    = ""    #License
    status      = ""    #Status of node
    
    def __exit__(self):
        print("Closing AMPQ conn")
        eventDisconnectAMPQ()
        print("Closing Database conn")
        disconnectDatabase()
        
    
    #COMMON QUEUE BROKER FUNCTIONS
    def eventConnectAMPQ(self, config):
        #TODO: Handle multithreaded channels, connection pools, and verify channel status somehow.
        
        print("Opening AMPQ connection")
        credes      = rabbit.PlainCredentials(config.mquser, config.mqpass)
        params      = rabbit.ConnectionParameters(host=config.mqhost, port=config.mqport, virtual_host=config.mq_vhost, credentials=credes) 
        connection  = rabbit.BlockingConnection(params)
        
        self.ampq   = connection.channel()
        print("Suscribing to 'core' exchange")
        self.ampq.exchange_declare(config.mq_exchange, config.mq_exchange_type, durable=True)
        
        print("AMPQ Connected")
        pass
    
    def eventDisconnectAMPQ(self):
        print("Disconnecting from AMPQ Broker")
        self.ampq.connection.close()
        pass
    
    def test_thread(self, config, test):
        self.ampq.channel.basic_publish(exchange=config.mq_exchange, routing_key=config.mq_general, body=str(test))
    
    
    #Suscribe to a queue
    def eventSuscribeToQueue(self, queueName):
        return
    
    def msgPublish(self, queue, event):
        return    
    
    
    def msgReceive(self):
       return       
    
    
    def msgProcess(self):
        return
    
    #STATUS VARS
    #Set current status of the Main Instance    
    def setStatus(self):
        return
    
    def getStatus(self):
        return
    
    #POLL LOCAL SERVER ENVIRONMENT
    #TODO - You must unify the local DYME_LOCAL folder on all servers (fusermount or use local SSD)
    def pollLocalServer(self):
        print(self.node_type +"Node is polling its local server")
        self.cpu_count = ps.cpu_count()
        self.cpu_freq  = ps.cpu_freq()[2]
        self.ram_total = ps.virtual_memory()[0]
        self.ram_free  = ps.virtual_memory()[1]
        self.swap_total= ps.swap_memory()[0]
        self.swap_free = ps.swap_memory()[2]
        self.disk_free = ps.disk_usage(self.dyme_local)[2]
        
        print("")
        print("  CPU: "+str(self.cpu_count)+" cores, at "+str(self.cpu_freq)+"Mhz")
        print("  RAM: "+self.convert_size(self.ram_total)+" total - "+self.convert_size(self.ram_free)+" Free")
        print("  HD:  "+self.convert_size(self.disk_free)+" of scratch disk left at "+self.dyme_local)
        print("")
        return
    
    #LICENSING
    def checkLicense(self):
        return
 
      
