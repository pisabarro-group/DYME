"""
Created on Wed Sep 28 16:59:18 2022

File:        dbreporter.py
Description: Outputs simulation trajectories and status into a remote database.
             Two Database Engines are suported. MongoDB and MySQL. This is the Database 
             reporting engine of the DYME platform. 
             
             Base class structure was taken from dcdreporter.py by Peter Eastman (OpenMM).

Provides:   DYMEReporter()

User specifies engine type, access credentials, database and remote IP
to create the DBMS connection. Database queries are handled via python DB Drivers.

--MongoDB--
Parses the simulation state (default) and into a JSON/BSON doc.
Inserts into a new document within a desired collection. If the 
database/collection don't exist, it creates both. Frame number is 
used as ID of the document within the collection.

--MYSQL-- TODO
Ideally MySQL output creates 3 relational tables. A table to store frame IDs, 
and a table to store atom attributes per frame. This uses the same data, 
but executes SQL inserts with peewee instead of pymongo's inserts.

Oct 1 2022: TODO: Create a parser to convert DB data back into an OpenMM state object.
This could be done in a dyme_utilities.py file.


Jul 2023: Added MD status variable updating.


Author:     
Pedro Manuel Guillem Gloria <pedro_manuel.guillem_gloria@tu-dresden.de>
Structural Bioinformatics Lab - BIOTEC - Pisabarro Group
Technische Universität Dresden
"""

from __future__ import absolute_import
__author__ = "Pedro Guillem"
__version__ = "1.0"

from math import isnan, isinf
from socket import gethostname
from datetime import datetime
from openmm import unit as u
from openmm.unit import nanometer
from openmm.unit import nanosecond
from time import time
import getpass
import subprocess
import re

#Our own
from DymeDB import DymeDB

VELUNIT = u.angstrom / u.picosecond
FRCUNIT = u.kilocalorie_per_mole / u.angstrom


class DYMEReporter(object):
    """
    DB Reporter outputs series of frames from a OpenMM Simulation to a remote DBMS.
    To use it, create a DYMEReporter, then add it to the Simulation's list of reporters.
    """
    
    #Constructor
    def __init__(self, project_id, mutantID, reportInterval=10000, dbtype="MongoDB"):
        """Create a DYMEReporter.

        Parameters
        ----------
        project_id: int
            Self explanatory            
        mutantID: int
            Self explanatory
        reportInterval : int
            The interval (in time steps) at which to write frames
        enforcePeriodicBox: bool
            Specifies whether particle positions should be translated so the center of every molecule
            lies in the same periodic box.  If None (the default), it will automatically decide whether
            to translate molecules based on whether the system being simulated uses periodic boundary
            conditions.
        stEnergy/Positions/Velocities/Forces: bool
            Specifies which component collections should be exported per particle
        dbtype : str
            DB Engine type (MongoDB or MySQL)
        """
        
        if project_id == "":
            print("Can't run reporter without a project ID")
            raise TypeError("Can't run reporter without a project ID")
            return 0

        if mutantID == "":
            print("Can't run reporter without a mutantID")
            raise TypeError("Can't run reporter without a project ID")
            return 0

        
        #Self Setters
        self._reportInterval = reportInterval
        self._enforcePeriodicBox = None
        self._dbtype = dbtype
        self._isConnected = False
        self.stEnergy     = True
        self.stPositions  = False 
        self.stVelocities = False
        self.stForces     = False
        self.project_id   = project_id
        self.mutantID     = mutantID
        self._step = True
        self._time = time
        self._potentialEnergy = True
        self._kineticEnergy = True
        self._totalEnergy = True
        self._temperature = True
        self._gpu = True
        self._volume = False
        self._density = False
        self._separator = ","
        self._totalMass = False
        self._hasInitialized = False
        self._needsPositions = False
        self._needsVelocities = False
        self._needsForces = False
        self._needEnergy = True
        self._energyUnit = u.kilocalories_per_mole
        self._densityUnit = u.grams/u.item/u.milliliter
        self._timeUnit = u.nanoseconds
        self._volumeUnit = u.angstroms**3
        self._initialDatetime = ""
        
        #Connect Database and store in self pointer
        if(dbtype == "MongoDB"):
           self.DB = DymeDB()
           self._isConnected = True
        else:
           try:            
              #TODO: Verify if MySQL connection is sane
              #self._client = MySQLDatabase(dbcredentials[4], **{'host': dbcredentials[2], 'sql_mode': 'PIPES_AS_CONCAT', 'charset': 'utf8', 'password': dbcredentials[1], 'user': dbcredentials[0], 'use_unicode': True})
              print("MySQL Driver is not yet implemented")
           except:
               print("MySql Error")
               
        #Fetch project Data 
        self.default_settings = self.DB.select_document("default_settings",{})
        self.project          = self.DB.select_document("projects",{"id_project": project_id})
        self.path = path      = self.default_settings["hpc_path"]+self.default_settings["project_dir"]
        self.projectpath = f'{path}/{project_id}/'
        self.mutantpath  = f'{path}/{project_id}/mutants/'
        self.inputs      = f'{path}/{project_id}/inputs/'
        self.outputs     = f'{path}/{project_id}/outputs/'  
        self._totalSteps = int(self.project["simulation"]['steps'])
            
        #Fetch local system data
        self.hostname = gethostname()

               
    #Destructor - Close DB connection
    def __del__(self):
        del self.DB
        print("Cleaning up.. Closing DB Connection")


    #STDOUT reporter
    def logToStdout(self, msg):
        print(msg)

    #////////////////////////////////////////////////////////////////////////////////////////
    #////////////////////////////////////////////////////////////////////////////////////////
    #////////////////////////////////////////////////////////////////////////////////////////
 
    def describeNextReport(self, simulation):
        """Get information about the next report this object will generate.
        Parameters
        ----------
        simulation : Simulation
            The Simulation to generate a report for
            
            Comes from P.Eastman and J.Swails. They have slightly different verstions 
            of this function. 
        """
        steps = self._reportInterval - simulation.currentStep % self._reportInterval
        return (steps, False, False, False, True)



    def report(self, simulation, state):
            """Generate a report and Store into the Database.
            
            Parameters
            ----------
            simulation : :class:`app.Simulation`
                The Simulation to generate a report for

            state : :class:`mm.State`
                The current state of the simulation
            """
            
            if not self._hasInitialized:
                self._initStatusDictionary()
                self._initializeConstants(simulation)
                self._initialClockTime = time()
                self._initialDatetime = datetime.now()
                self._initialSimulationTime = state.getTime()
                self._initialSteps = simulation.currentStep
                self._hasInitialized = True
    
            # Check for errors
            self._checkForErrors(simulation, state)
    
            # Query for the values
            values_dict = self._constructReportValues(simulation, state)
    
            # Write the values TO THE DB!
            self.updateStatusVars(values_dict)
    
    
    def _constructReportValues(self, simulation, state):
            """
            Query the simulation for the current state of our observables of
            interest.
            Parameters
            ----------
            simulation : Simulation
                The Simulation object to generate a report for
            state : State
                The current state of the simulation object
            Returns: A list of values summarizing the current state of
            the simulation, to be printed or saved. Each element in the list
            corresponds to one of the columns in the resulting CSV file.
            """
            
            values = {
                "path_outputs": self.outputs, 
                "path_inputs": self.inputs, 
                "md_node": self.hostname, 
                "md_gpu_type": "",
                "md_gpu_index": "",
                "md_gpu_memory": "", 
                "md_date_start": self._initialDatetime, 
                "md_date_end": "",
                "md_last_temperature": 0, 
                "md_remaining_time": 0,
                "md_elapsed_time": 0,
                "md_remaining_time_seconds": 0,
                "md_elapsed_time_seconds": 0,
                "md_ns_perday": 0,
                "md_current_step": 0,
                "md_progress_percentage": 0, 
                "md_potentiale": 0,
                "md_kinetice": 0,
                "md_totale": 0,
                "scavenger_node": "", 
                "scavenger_current_step": "",
                "scavenger_start_time": "", 
                "scavenger_finish_time": "",
                "scavenger_start_time_seconds": "", 
                "scavenger_finish_time_seconds": "",  
                "scavenger_elapsed": 0, 
                "scavenger_progress_percentage": 0
            }      
            
            
            ke = state.getKineticEnergy() #Get kinetic energy
            pe = state.getPotentialEnergy() #get Potential Energy
            temp = 2 * ke / (self._dof * u.MOLAR_GAS_CONSTANT_R) #Get temperature
            pla = simulation.context.getPlatform().getName() #Get platform (CUDA/OPENCL)
            
            gpu = simulation.context.getPlatform().getPropertyValue(simulation.context,'DeviceName') #CardName
            gpu_num = simulation.context.getPlatform().getPropertyValue(simulation.context,'DeviceIndex') #Index
            clockTime = time()
 
            #TIME VS STEPS RELATED STUFF
            values["md_current_step"] = simulation.currentStep
            values["md_progress_percentage"] = str(round(100.0*simulation.currentStep/self._totalSteps, 2))
           
            #NOTHING'S GONNA TAKE DAYS... REMOVING ELAPSEDAYS
            elapsedDays = (clockTime-self._initialClockTime)/86400.0
            elapsedNs = (state.getTime()-self._initialSimulationTime).value_in_unit(u.nanosecond)
            if elapsedDays > 0.0:
                values["md_ns_perday"] = '%.3g' % (elapsedNs/elapsedDays)
            else:
                values["md_ns_perday"] = '--'
            
            #Get elapsed time - Taken from origonal Statereporter from P.Eastman
            elapsedSeconds = int(clockTime-self._initialClockTime)
            elapsedSteps = simulation.currentStep-self._initialSteps
            if elapsedSteps > 0:
                estimatedTotalSeconds = (self._totalSteps-self._initialSteps)*elapsedSeconds/elapsedSteps
                remainingSeconds = int(estimatedTotalSeconds-elapsedSeconds)
                values["md_remaining_time"] = self.display_time(remainingSeconds, 2)
            else:
                remainingSeconds = 0
                values["md_remaining_time"] = "calculating..."
                                
            #EVERYTHING ELSE
            
            values["md_elapsed_time"]           = self.display_time(elapsedSeconds, 2)
            values["md_remaining_time_seconds"] = remainingSeconds
            values["md_elapsed_time_seconds"]   = elapsedSeconds
            
            #Energies
            values["md_potentiale"]     = pe.value_in_unit(self._energyUnit)
            values["md_kinetice"]       = ke.value_in_unit(self._energyUnit)
            values["md_totale"]         = (pe + ke).value_in_unit(self._energyUnit)
            values["md_last_temperature"] = temp.value_in_unit(u.kelvin)
            
            #GPU TYPE AND MEMORY... We need to wait for the simulation object before getting the used mem.. 
            # so we updatre the GPU type here. We can do this in MD.py, but i'm just lazy
            
            values["md_gpu_type"] = gpu
            values["md_gpu_index"] = gpu_num
            
            if pla == "CUDA": #TODO: Enable OPENCL gather routines
                try:
                    usage = self.get_gpu_usage()
                    values["md_gpu_memory"] = usage[str(gpu_num)]["used"] # in Mb
                except:
                    values["md_gpu_memory"] = "0"
                    
            return values
    
    
    
    
    
    def updateStatusVars(self, values):
        """ Update the mutant table with the new information.
            Insert a log record in the mutant_md_logs table
        """
        #Execute actual update of database values
        q  = {"id_project": self.project_id, "mutantID": self.mutantID}
        newvalues = {"$set": { "status_vars":  values }}
        self.DB.dbtable_mutants.update_one(q, newvalues)  
 
 
 
    def _initStatusDictionary(self):
        #Create basic status vars dictionary in a mutant record            
        if not self._hasInitialized:        
            #UPDATE where clase
            q  = {"id_project": self.project_id, "mutantID": self.mutantID}
            
            #Data sub dict to add
            var = {
                "path_outputs": self.outputs, 
                "path_inputs": self.inputs, 
                "md_node": self.hostname, 
                "md_gpu_type": "NA",
                "md_gpu_index": 0,
                "md_gpu_memory": "NA",
                "md_date_start": datetime.now(), 
                "md_date_end": "", 
                "md_last_temperature": 0, 
                "md_remaining_time": 0,
                "md_elapsed_time": 0,
                "md_ns_perday": 0,
                "md_current_step": 0,
                "md_progress_percentage": 0, 
                "md_potentiale": 0,
                "md_kinetice": 0,
                "md_totale": 0,               
                "scavenger_node": "", 
                "scavenger_current_step": "",
                "scavenger_start_time": "", 
                "scavenger_finish_time": "", 
                "scavenger_elapsed": 0, 
                "scavenger_progress_percentage": 0
            }
            #Build Update dict
            newvalues = {"$set": { 'status_vars':  var}}
            self.DB.dbtable_mutants.update_one(q, newvalues)        
        
    
    
    def display_time(self, seconds, granularity=2):
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
    
    
    
    
    def _initializeConstants(self, simulation):
            """
            Initialize a set of constants required for the reports
            Parameters
            ----------
            simulation : Simulation
                The simulation to generate a report for
            """
            import openmm as mm
            system = simulation.system
            frclist = system.getForces()
            if self._temperature:
                # Compute the number of degrees of freedom.
                dof = 0
                for i in range(system.getNumParticles()):
                    if system.getParticleMass(i) > 0*u.dalton:
                        dof += 3
                dof -= system.getNumConstraints()
                if any(isinstance(frc, mm.CMMotionRemover) for frc in frclist):
                    dof -= 3
                self._dof = dof
            if self._density:
                if self._totalMass is None:
                    # Compute the total system mass.
                    self._totalMass = 0*u.dalton
                    for i in range(system.getNumParticles()):
                        self._totalMass += system.getParticleMass(i)
                elif not u.is_quantity(self._totalMass):
                    self._totalMass = self._totalMass*u.dalton
  
   
    def _checkForErrors(self, simulation, state):
            """Check for errors in the current state of the simulation
            Parameters
            ----------
            simulation : :class:`app.Simulation`
                The Simulation to generate a report for
            state : :class:`State`
                The current state of the simulation
            """
            if self._needEnergy:
                energy = state.getKineticEnergy() + state.getPotentialEnergy()
                if isnan(energy._value):
                    raise ValueError('Energy is NaN') # pragma: no cover
                if isinf(energy._value):
                    raise ValueError('Energy is infinite') # pragma: no cover

            
    def finalize(self):
        """
        This used to close any open files
        """
        pass            

    
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
        gpu_usage = {gpu_id: {"used": 0, "used_by_others": 0, "total": int(total)}
            for gpu_id, total in total_memory.items()}
    
        # Use nvidia-smi to get GPU memory usage of each process
        command = ["nvidia-smi", "pmon", "-s", "m", "-c", "1"]
        output = subprocess.check_output(command).decode("utf-8")
        for row in output.strip().split("\n"):
            if row.startswith("#"): continue
    
            #gpu_id, pid, type, mb, command = row.split('')
            gpu_id, pid, type, mb, command = list(filter(None, re.split(r'\s{2,}', row)))
    
            # Special case to skip weird output when no process is running on GPU
            if pid == "-": continue
    
            gpu_usage[gpu_id]["used"] += int(mb)
    
            # If the GPU user is different from us
            if pid_user[pid] != current_user:
                gpu_usage[gpu_id]["used_by_others"] += int(mb)
    
        #print(gpu_usage)
        return gpu_usage
    
