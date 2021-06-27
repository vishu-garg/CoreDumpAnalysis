from ConsoleLogs import logConsole
from WarningLog import logWarning
import re
import subprocess
import sys
import os
from pprint import pprint

from CD_Module import CD_Module

from ErrorLog import logErr

GDBLibraryRegex= r"0x([\da-f]+)\s+0x([\da-f]+)\s+\w*\s+(?:\(\*\)\s+)?(.*)"
ReadELFSectionRegex= r"\.\w+\s*PROGBITS\s*([\da-f]+)\s*([\da-f]+)"

class SharedLibAnalyzer:
    def __init__(self) -> None:
        pass

    def AnalyzeGDBoutput(self,gdbOutput,gdbErr,Result):

        #  Check for GDB error
        if len(gdbErr) != 0:
            # print('Err while analyzing GDB...')
            logErr('Error while analyzing GDB')
            flg=0
            for errs in gdbErr:
                # print(errs)
                logErr(errs)
                if errs.count("raise.c")==0:
                    flg=1
            if flg==1:
                sys.exit(2)
            else:
                # print('Warning: Ignoring Raise Exception\n')
                logWarning('Ignoring Raise Exception')

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
                # print('Shared Library: 0x'+startAddr+' - 0x'+endAddr+': '+library)
                
                module = CD_Module()
                StartAddr = int(startAddr,16)
                EndAddr = int(endAddr,16)
                FilePath = library
                FileName = os.path.basename(library)
                LocalPath = os.path.join(SharedLibPath,FileName)
                if not os.path.isfile(LocalPath):
                #   print("Warning : Module "+FilePath +" is not found in local shared library folder")
                    logWarning(str('Module'+FilePath+' is not found in local shared library folder'))
                    LocalPath="Not Found Locally"
                FileSize = os.path.getsize(library)
                module.generateModule(StartAddr,EndAddr,FilePath,FileName,LocalPath,FileSize)
                modules.append(module)


        #  Resolve Symlinks
        for module in modules:
            try:
                p1 = subprocess.Popen(["readlink","-f",module.FilePath],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            except Exception as e:
                # print(e.args[1])
                logErr(e.args[1])
                sys.exit(2)
            else:
                output=p1.stdout.readline().decode()
                path=output.strip()
                module.FilePath=path
                module.FileName=os.path.basename(path)

        # Add backingFiles
        for module in modules:
            try:
                p1 = subprocess.Popen(["readelf","-S",module.FilePath],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            except Exception as e:
                # print(e.args[1])
                logErr(e.args[1])
                sys.exit(2)
            else:
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

                if len(err)>0:
                    # print("Error while reading Shared libreary")
                    logErr("Error while reading Shared libreary")
                    for er in err:
                        # print(er)
                        logErr(er)
                    sys.exit(2)
                
                for line in output:
                    if ".text" in line:
                        x= re.search(ReadELFSectionRegex,line)
                        if x:
                            offset = int(x.group(2),16)
                            module.StartAddr-=offset
                            break;
            
            

        # Add Modules into the Result
        Result.Modules=modules

        return

    def InputGDBCommands(self,p1,Result):
        # print(Result.ExecutablePath)
        # print(Result.coreDumpInfo['FilePath'])
        p1.stdin.write(('file "'+Result.ExecutablePath+'"\n').encode())
        p1.stdin.write(bytes('core-file '+Result.coreDumpInfo['FilePath']+'\n','utf-8'))
        p1.stdin.write(bytes('info sharedlibrary'+'\n','utf-8'))
        p1.stdin.write('quit \n'.encode())
        p1.stdin.close()

    def ReadGDBOutput(self,p1):
        gdbOutput=[]
        gdbErr=[]
        while True:
            line = p1.stdout.readline()
            if line:
                curLine=line.decode()
                gdbOutput.append(curLine)
            else:
                break
        while True:
            line = p1.stderr.readline()
            if line:
                curline=line.decode()
                if re.match("warning:",curline):
                    logWarning(curline)
                    continue
                gdbErr.append(curline)
            else:
                break;
        return gdbOutput, gdbErr

    def Analyze(self,Result):
        try:
            p1=subprocess.Popen(["gdb"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            self.InputGDBCommands(p1,Result)
            Exception("error while giving input to GDB")
        except Exception as e:
            # print(e.args[1])
            logErr(e.args[1])
            sys.exit(2)
        else:   
            gdbOutput , gdbErr=self.ReadGDBOutput(p1)
            logConsole('Analysing GDB output...')
            # print('Analysing GDB output...')
            self.AnalyzeGDBoutput(gdbOutput,gdbErr,Result)


        