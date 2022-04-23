'''
Script:  Searching the Filesystem For a Match + Logging
Date:    April 2022
Version: 1.0
Purpose: Given a directory, walk the filesytem to search
         for either Filename, File Extension, or File Hash
         and display the results that match with a prettytable.
         Log information, warning, error, and critical messages 
         to the ScriptLog.txt file.
'''

''' IMPORT STANDARD LIBRARIES '''
import os         # File System Methods
import sys        # System Methods
import time       # Time Conversion Methods
import datetime   # Represents dates and times with values
import hashlib    # Hash Messages
import logging    # Write status messages to a file
import platform   # Access platform data
import socket     # Will be used to identify hostname & ip address
import re         #
import uuid       # Identify unique info (mac address)

''' IMPORT 3RD PARTY LIBRARIES '''
from prettytable import PrettyTable  # pip install prettytable
                                     # display data in table layout

import pyfiglet                      # pip install pyfiglet
                                     # Print ASCII Art

import psutil                        # pip instal psutil
                                     # access system details and process utilities

''' PSEUDO CONSTANTS '''
asciiBanner = pyfiglet.figlet_format("FILESYSTEM SEARCHER", font="slant") # Setup for Banner Art

tbl = PrettyTable(['Hashmatch','ExtMatch','PathMatch','FileName','FileType','AbsPath','FileSize','LastModified','LastAccess','CreatedTime','HASH']) # Defining prettytable columns

filesProcessed = 0
filesMatched = 0

''' LOCAL FUNCTIONS '''
def GetSystemInfo():
    ''' 
        obtain system info
        to include in the logs
        
        log any occured errors
    '''    
    try:
        info={}
        info['ip-address']=socket.gethostbyname(socket.gethostname())
        info['mac-address']=':'.join(re.findall('..', '%012x' % uuid.getnode()))        
        info['platform']=platform.system()
        info['platform-release']=platform.release()
        info['platform-version']=platform.version()
        info['hostname']=socket.gethostname()
        info['architecture']=platform.machine()
        info['processor']=platform.processor()
        info['ram capacity']=str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
        return info
    except Exception as e:
        logging.warning(e)

def GetFileMetaData(fileName):
    ''' 
        obtain filesystem metadata
        from the specified file
        specifically, fileSize and MAC Times
        
        convert to UTC time
        
        Group MAC Times in a List
        
        Get SHA256 hash of eachFile
        
        Search for file hash match
        Search for extension match with .lower
        Search for filename match with .lower
        
        return True, None, fileSize and MacTimeList
    '''
    try:
        
        metaData         = os.stat(fileName)       # Use the stat method to obtain meta data
        fileSize         = metaData.st_size        # Extract fileSize and MAC Times
        timeLastAccess   = metaData.st_atime
        timeLastModified = metaData.st_mtime
        timeCreated      = metaData.st_ctime
        
        modTime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(timeLastModified))
        accTime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(timeLastAccess))               
        creTime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(timeCreated))
        
        with open(absPath, 'rb') as hashFile:       # Acquiring the SHA-256 hash value
            fileContents = hashFile.read()
            hashObj = hashlib.sha256()
            hashObj.update(fileContents)
            hexDigest = hashObj.hexdigest()
            if hexDigest == targetHash:
                hashMatch = "yes"
            else:
                hashMatch = "no"
                
        if targetExt.lower() in absPath.lower():
            extMatch = 'yes'
        else:
            extMatch = 'no'
                        
        if targetPath.lower() in absPath.lower():
            pathMatch = 'yes'
        else:
            pathMatch = 'no'        
        
        macTimeList = [modTime, accTime, creTime]   # Group the MAC Times in a List
        return True, None, fileSize, macTimeList, hexDigest, hashMatch, extMatch, pathMatch
    
    except Exception as err:
        logging.warning(str(err)+"\n")        
        return False, str(err), None, None, None, None, None, None    

''' MAIN ENTRY POINT '''

if __name__ == '__main__':
    
    startTime = time.time()
    
    logging.basicConfig(filename='ScriptLog.txt',level=logging.DEBUG,format='%(asctime)s - %(process)d- %(levelname)s- %(message)s')
    
    logging.info("="*39)
    logging.info("Script Started: LoggingFilesystemSearch")
    logging.info("="*39+"\n")
    
    logging.info("*"*9+" System Information "+"*"*10)
    systemInfoDict = GetSystemInfo()
    for key, value in systemInfoDict.items():
        logging.info(key+": "+value)
    logging.info("*"*39+"\n")
    
    print(asciiBanner)
    
    while True:
        targetDIR = input("Enter a Directory: ")                 # User inputs a starting directory
        if not os.path.isdir(targetDIR):                         # Checking for valid input
            logging.warning("User Specified Invalid Directory: "+targetDIR)
            print()                                              # User is asked for new input if invalid Dir is input
            print("Warning: INVALID DIRECTORY - Enter a Valid Directory to Begin Search")
            print()
            continue
        else:
            logging.info("User Specified Valid Directory: "+targetDIR)
            break
        
    targetPath = input("Enter a Filename to Match: ")
    logging.info("User Specified Path: "+targetPath)
    
    targetExt = input("Enter an Extension to Match: ")           # User defines the search criteria
    logging.info("User Specified Extension: "+targetExt)                 # inputs are logged
    
    targetHash = input("Enter a Hash to Match: ")
    logging.info("User Specified Hash: "+targetHash+"\n")
    
    print()
    print("Directory: ", targetDIR)
    print("Path:      ", targetPath)
    print("Extension: ", targetExt)                              # Displaying the search criteria to match
    print("Hash:      ", targetHash)
    print()
    
    startSearch = time.time()
        
    try:
        
        for root, dirs, fileList in os.walk(targetDIR):     # Walking the filesystem for the specified direcotry
            
            for eachFile in fileList:
                filesProcessed += 1
                path = os.path.join(root, eachFile)
                absPath = os.path.abspath(path)             # Get the absolute path               
                
                success, errInfo, fileSize, macTimeList, hexDigest, hashMatch, extMatch, pathMatch = GetFileMetaData(path)   # Running each file through the local function
                
                if success:
                    
                    if os.path.isfile(path):
                        fileType = "File"
                    elif os.path.isdir(path):
                        fileType = "Directory"              # Spcifying the file type of each file
                    elif os.path.islink(path):
                        fileType = "Link"
                    else:
                        fileType = "Unknown"
                else:
                    print("Warning: ", errInfo, "\n")
                
                if hashMatch == 'yes' or extMatch == 'yes' or pathMatch == 'yes':
                    filesMatched += 1
                    tbl.add_row( [ hashMatch, extMatch, pathMatch, eachFile, fileType, absPath, fileSize, macTimeList[0], macTimeList[1], macTimeList[2], hexDigest] )  # Adding the captured information to the prettytable, only if at least 1 match is found
                    logging.critical("Match Found: ")
                    logging.critical("File Name: "+eachFile)
                    logging.critical("File Path: "+absPath)
                    logging.critical("File Type: "+fileType)
                    logging.critical("File Size: "+str(fileSize)+" bytes")
                    logging.critical("File Hash: "+hexDigest)
                    logging.critical("Last Modified: "+macTimeList[0])
                    logging.critical("Last Accessed: "+macTimeList[1])
                    logging.critical("Time Created:  "+macTimeList[2])
                    logging.critical("-"*34)
                    logging.critical("Ext Match:  "+extMatch)
                    logging.critical("Path Match: "+pathMatch)
                    logging.critical("Hash Match: "+hashMatch+"\n")
        
        endSearch = time.time()
        elapsedSearch = endSearch - startSearch

        tbl.align = "l"
        print(tbl.get_string(sortby="FileSize", reversesort=True))  # Printing the prettytable
        print()
        print("Search Time:", elapsedSearch, "seconds")
        print("Files Processed:", filesProcessed)                   # Printing Search Info
        print("Files Matched:", filesMatched)
        
                
    except Exception as err:
        print("\n\nScript Aborted     ", "Exception =     ", err)
        logging.error("Description: "+str(err))
        logging.error("File Name: "+eachFile)
        logging.error("File Path: "+absPath)
        logging.error("File Type: "+fileType)
        logging.error("File Size: "+str(fileSize)+" bytes")
        logging.error("File Hash: "+hexDigest)
        logging.error("Last Modified: "+macTimeList[0])
        logging.error("Last Accessed: "+macTimeList[1])
        logging.error("Time Created:  "+macTimeList[2]+"\n")        
    
    endTime = time.time()
    elapsedTime = int(endTime - startTime)
    deltaTime = datetime.timedelta(seconds=elapsedTime)
    
    logging.info("Script Information: ")
    logging.info("Ran From: "+os.getcwd())
    logging.info("Run Time: "+str(deltaTime))
    logging.info("Search Time: "+str(elapsedSearch)+" seconds")
    logging.info("Files Processed: "+str(filesProcessed))
    logging.info("Files Matched: "+str(filesMatched)+"\n")