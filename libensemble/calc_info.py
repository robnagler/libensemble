"""
Module for storing and managing statistics for each calculation.

This includes creating the statistics (or calc summary) file.

"""
import time
import datetime
import itertools
import os

from libensemble.message_numbers import EVAL_SIM_TAG, EVAL_GEN_TAG

#Maybe these should be set in here - and make manager signals diff? Would mean called by sim_func...
#Currently get from message_numbers
from libensemble.message_numbers import UNSET_TAG
from libensemble.message_numbers import WORKER_KILL
from libensemble.message_numbers import WORKER_KILL_ON_ERR
from libensemble.message_numbers import WORKER_KILL_ON_TIMEOUT
from libensemble.message_numbers import JOB_FAILED 
from libensemble.message_numbers import WORKER_DONE
from libensemble.message_numbers import MAN_SIGNAL_FINISH
from libensemble.message_numbers import MAN_SIGNAL_KILL
from libensemble.message_numbers import CALC_EXCEPTION

class CalcInfo():
    """A class to store and manage statistics for each calculation.
    
    An object of this class represents the statistics for a given calculation.
    
    **Class Attributes:**

    :cvar string stat_file:
        A class attribute holding the name of the global summary file (default: 'libe_summary.txt')
        
    :cvar string worker_statfile:
        A class attribute holding the name of the current workers summary file
        (default: Initially None, but is set to <stat_file>.w<workerID> when the file is created)
        
    :cvar boolean keep_worker_stat_files:
        A class attribute determining whether worker stat files are kept after merging
        to global summary file (default: False).


    **Object Attributes:**
    
    :ivar float time: Calculation run-time 
    :ivar string date_start: Calculation start date 
    :ivar string date_end: Calculation end date     
    :ivar int calc_type: Type flag:EVAL_SIM_TAG/EVAL_GEN_TAG
    :ivar int id: Auto-generated ID for this calc (unique within Worker)
    :ivar string status: "Description of the status of this calc"

    """
    newid = itertools.count()
    stat_file = 'libe_summary.txt'
    worker_statfile = None
    keep_worker_stat_files = False

    @staticmethod
    def set_statfile_name(name):
        """Change the name ofr the statistics file"""
        CalcInfo.stat_file = name
    
    @staticmethod
    def smart_sort(l):
        """ Sort the given iterable in the way that humans expect.
        
        For example: Worker10 comes after Worker9. No padding required
        """ 
        import re        
        convert = lambda text: int(text) if text.isdigit() else text 
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
        return sorted(l, key = alphanum_key)

    @staticmethod
    def create_worker_statfile(workerID):
        """Create the statistics file"""
        CalcInfo.worker_statfile = CalcInfo.stat_file + '.w' + str(workerID)
        with open(CalcInfo.worker_statfile,'w') as f:
            f.write("Worker %d:\n" % (workerID))        

    @staticmethod
    def add_calc_worker_statfile(calc):
        """Add a new calculation to the statistics file"""
        with open(CalcInfo.worker_statfile,'a') as f:
            calc.print_calc(f)

    @staticmethod
    def merge_statfiles():
        """Merge the stat files of each worker into one master file"""
        import glob
        worker_stat_files = CalcInfo.stat_file + '.w'
        stat_files = CalcInfo.smart_sort(glob.glob(worker_stat_files + '*'))        
        with open(CalcInfo.stat_file, 'w') as outfile:
            for fname in stat_files:
                with open(fname) as infile:
                    outfile.write(infile.read())
        for file in stat_files:
            if not CalcInfo.keep_worker_stat_files:
                os.remove(file)        
    
    def __init__(self):
        """Create a new CalcInfo object
        
        A new CalcInfo object is created for each calculation.
        """
        self.time = 0.0
        self.start = 0.0
        self.end = 0.0
        self.date_start = None
        self.date_end = None        
        self.calc_type = None        
        self.id = next(CalcInfo.newid)
        self.status = "Not complete" 
    
    def start_timer(self):
        """Start the timer and record datestamp (normally for a calculation)"""
        self.start = time.time()
        self.date_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def stop_timer(self):
        """Stop the timer and record datestamp (normally for a calculation) and set total run time"""        
        self.end = time.time()
        self.date_end = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        #increment so can start and stop repeatedly
        self.time += self.end - self.start
        
    def print_calc(self, fileH):
        """Print a calculation summary.
        
        This is called by add_calc_worker_statfile to add to statistics file.
        
        Parameters
        ----------
        
        fileH: file handle:
            File to print calc statistics to.
            
        """
        fileH.write("   Calc %d: %s Time: %.2f Start: %s End: %s Status: %s\n" % (self.id, self.get_type() ,self.time, self.date_start, self.date_end, self.status))

    #Should use message_numbers - except i want to separate type for being just a tag.
    def get_type(self):
        """Returns the calculation type as a string.
        
        Converts self.calc_type to string. self.calc_type should have been set by the worker"""
        if self.calc_type==EVAL_SIM_TAG:
            return 'sim'
        elif self.calc_type==EVAL_GEN_TAG:
            return 'gen' 
        elif self.calc_type==None:
            return 'No type set'
        else:
            return 'Unknown type'

    def set_calc_status(self, calc_status_flag):
        """Set status description for this calc
        
        Parameters
        ----------
        calc_status_flag: int
            Integer representing status of calc
            
        Return: String:
            String describing job status
        
        """

        #Prob should store both flag and description (as string)
        if calc_status_flag is None:
            self.status = "Unknown Status"
            return
        
        if calc_status_flag == MAN_SIGNAL_FINISH:   #Think these should only be used for message tags?
            self.status = "Manager killed on finish" #Currently a string/description
        elif calc_status_flag == MAN_SIGNAL_KILL: 
            self.status = "Manager killed job"
        elif calc_status_flag == WORKER_KILL_ON_ERR:
            self.status = "Worker killed job on Error"
        elif calc_status_flag == WORKER_KILL_ON_TIMEOUT:
            self.status = "Worker killed job on Timeout"   
        elif calc_status_flag == WORKER_KILL:
            self.status = "Worker killed"               
        elif calc_status_flag == JOB_FAILED:
            self.status = "Job Failed"
        elif calc_status_flag == WORKER_DONE:
            self.status = "Completed"            
        elif calc_status_flag == CALC_EXCEPTION:
            self.status = "Exception occurred"
        else:
            #For now assuming if not got an error - it was ok
            self.status = "Completed"
            #self.status = "Status Unknown"
