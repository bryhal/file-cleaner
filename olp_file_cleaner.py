#!/usr/bin/env python

"""
File Cleaner v1.0.0
remove files of defined type after defined age (in days)
Bryan Halstead Aug 22 2013
Aug 24 - add test_mode - view results without deletion or log entry
Aug 25 - renamed from 'olp_eps_cleaner' - now more general purpose and uses 
         config file
"""

import fnmatch
import os
import string
import sys
import time
import datetime
from math import log
import ConfigParser

#UTILITY FUNCTIONS
##################

# Human Friendly File Sizes
unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])
def sizeof_fmt(num):
    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'

# maps config values to a  dictionary
def config_section_map(section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

# silly little quit routine
def done():
    print "Change test_mode to False to execute the file deletions"
    print "Bye. Have a super duper day"
    sys.exit(0)
    
#################

# setup configuration values  - set the config.read() path and view .cfg for instructions
config =  ConfigParser.ConfigParser()
config.read('./olp_file_cleaner.cfg')
# Normally no edits below this line
test_mode = config.getboolean('Global', 'test_mode')
log_file = config.get('Global', 'log_file')

settings_dict = {}
for section in config.sections():
    if section != 'Global': # not interested in Global anymore
        settings_dict[section] = config_section_map(section)  
# print test_mode
# print log_file_name
# print settings_dict
# sys.exit()
#print settings_dict['LF_EPS_Files']['file_type']

#################
log_out = []
space_freed = 0

if test_mode:
    print "Please wait..."

for working_dir in settings_dict:

    #print settings_dict[working_dir]['file_dir']
    file_dir = settings_dict[working_dir]['file_dir']
    file_type = settings_dict[working_dir]['file_type']
    days = int(settings_dict[working_dir]['days'])
 
    # initialize some variables
    files = []
    age = days * 86400
    file_count  = 0
    file_size = 0
    total_size = 0
    file_total_size = 0
    
    
    for root, dirnames, filenames in os.walk(file_dir):
        for filename in fnmatch.filter(filenames, file_type):
            now = time.time()
            filepath = os.path.join(root, filename)
            modified = os.stat(filepath).st_mtime
            file_size = os.stat(filepath).st_size
            if modified < now - age:
                files.append(filepath)
                total_size =  file_size + total_size
                file_count += 1
            
    if files:
        for deletable_file in files:
            if os.path.isfile(deletable_file) and not test_mode:
                os.remove(deletable_file)
    
    if file_count > 0:
        file_total_size = sizeof_fmt(total_size)
        space_freed = total_size + space_freed
        time_stamp = time.asctime( time.localtime(time.time()))
        log_out.append("%s - Deleted %s files older than %s days totalling %s - %s \n" % (time_stamp, file_count, days, file_total_size, working_dir))
    else:
        time_stamp = time.asctime( time.localtime(time.time()))
        log_out.append("%s - No files older than %s days found - %s \n" % (time_stamp, days, working_dir))

	
summary_line = "%s - %s of disk space freed \n" % (time_stamp, sizeof_fmt(space_freed))
        
if test_mode:
    for line in log_out:
        print line
    print summary_line
    print "Running in test mode - no files were removed and no log entry was made"
    done()
else:
    log = open(log_file, 'a')
    for line in log_out:
        log.write(line)
    log.write(summary_line)
    log.close()
    sys.exit(0)

