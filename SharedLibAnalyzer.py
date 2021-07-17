from ConsoleLogs import logConsole
from WarningLog import logWarning
import re
import subprocess
import sys
import os
from pprint import pprint

from CD_Module import CD_Module
from config import SYS_ROOT

from ErrorLog import logErr

GDBLibraryRegex= r"0x([\da-f]+)\s+0x([\da-f]+)\s+\w*\s+(?:\(\*\)\s+)?(.*)"
ReadELFSectionRegex= r"\.\w+\s*PROGBITS\s*([\da-f]+)\s*([\da-f]+)"



"""This class provides the information about 
the shared libraries which were present in the
process during crash"""

class SharedLibAnalyzer:
    def __init__(self) -> None:
        pass



    """This function will parse the information from GDB output"""
    def AnalyzeGDBoutput(self,gdbOutput,gdbErr,Result):

        #  Check for GDB error
        if len(gdbErr) != 0:
            logErr('Error while analyzing GDB')
            flg=0
            for errs in gdbErr:
                logErr(errs)
                

        #  Extract GDB modules
        modules=[]
        SharedLibPath = Result.directoryInfo['SharedLibPath']
        for line in gdbOutput:
            x=re.match(GDBLibraryRegex,line)
            if x:
                startAddr = x.group(1)
                endAddr = x.group(2)
                library = x.group(3)
                logConsole('Shared Library: 0x'+startAddr+' - 0x'+endAddr+': '+library)
                
                module = CD_Module()
                StartAddr = int(startAddr,16)
                EndAddr = int(endAddr,16)
                FilePath = library
                FileName = os.path.basename(library)
                LocalPath = os.path.join(SharedLibPath,FileName)
                if not os.path.isfile(LocalPath):
                    logWarning(str('Module'+FilePath+' is not found in local shared library folder'))
                    LocalPath="Not Found Locally"
                FileSize = os.path.getsize(library)
                module.generateModule(StartAddr,EndAddr,FilePath,FileName,LocalPath,FileSize)
                modules.append(module)

        #  Resolve Symlinks
        for module in modules:
            p1 = subprocess.Popen(["readlink","-f",module.FilePath],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            output=p1.stdout.readline().decode()
            path=output.strip()
            module.FilePath=path
            module.FileName=os.path.basename(path)

        """ The address that we got from GDB involves the offsets in them,
             we need to reduce these offsets to get the bases address 
             of each module"""
        # Add backingFiles
        for module in modules:
            p1 = subprocess.Popen(["readelf","-S",module.FilePath],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            output=[]
            err=[]
            while True:
                line=p1.stdout.readline()
                if line:
                    line=line.decode()
                    output.append(line)
                else:
                    break

                while True:
                    line= p1.stderr.readline()
                    if line:
                        line=line.decode()
                        if re.match("warning:",line):
                            logWarning(line)
                            continue
                        err.append(line)
                    else:
                        break
                
                for line in output:
                    if ".text" in line:
                        x= re.search(ReadELFSectionRegex,line)
                        if x:
                            offset = int(x.group(2),16)
                            #reduce offset from the start address
                            module.StartAddr-=offset
                            break;
            

        # Add Modules into the Result
        Result.Modules=modules

        return



    """ We use the "info sharedlibrary"  command
        the command is build in GDB
        gives information about the shared libraries 
        loaded in core file.
    """
    def InputGDBCommands(self,p1,Result):
        p1.stdin.write(('set sysroot '+SYS_ROOT+'\n').encode())
        p1.stdin.write(('set solib-search-path '+Result.directoryInfo["SharedLibPath"]+' \n').encode())
        p1.stdin.write(('file "'+Result.ExecutablePath+'"\n').encode())
        p1.stdin.write(bytes('core-file '+Result.coreDumpInfo['FilePath']+'\n','utf-8'))
        p1.stdin.write(bytes('info sharedlibrary'+'\n','utf-8'))
        p1.stdin.write('quit \n'.encode())
        p1.stdin.close()



    """Here we read the GDB output and store it for further analysis"""

    def ReadGDBOutput(self,p1):
        gdbOutput=[]
        gdbErr=[]
        # print(p1.stdout.readlines())
        while True:
            line = p1.stdout.readline()
            if line:
                try:
                    curLine=line.decode()
                    gdbOutput.append(curLine)
                except:
                    pass
            else:
                break
        while True:
            line = p1.stderr.readline()
            if line:
                curline=line.decode()
                if curline.strip()=="":
                    continue
                if re.match("warning:",curline):
                    logWarning(curline)
                    continue
                gdbErr.append(curline)
            else:
                break;
        return gdbOutput, gdbErr


    """Entry function of this class
      
        It does follwing things:
            Spwan a subprocess and enter GDB commands in it
            Read the output/ errors
            Parse the information about shared libraries

        We store the following info about each module/library:
            1. Start Address
            2. End Address
            3. Size of module
            4. FilePath: (Path used by GDB)
            5. FileName
            6. LocalPath: (Local Path for module in sharedlib/ folder)
    """

    def Analyze(self,Result):
        #Open the subproecess to call GDB from it
        p1=subprocess.Popen(["gdb-multiarch"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        
        #Enter commands in GDB
        self.InputGDBCommands(p1,Result)

        #Read the ouput of GDB
        gdbOutput , gdbErr=self.ReadGDBOutput(p1)
        
        #Analyse the output to parse the modules' information
        logConsole('Analysing GDB output...')
        self.AnalyzeGDBoutput(gdbOutput,gdbErr,Result)
        


        