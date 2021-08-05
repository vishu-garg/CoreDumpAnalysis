from Logs import getWarningLogger,getConsoleLogger,logconsole,getErrLogger,logerr,logwarning
import re
import subprocess
from config import SYS_ROOT
import sys
sigInfoRegex= r"info.si_signo:\s+(\d+)"
ErroNoRegex= r"info.si_errno:\s+(\d+)"
pgrpInfoRegex= r"pgrp:\s+(\d+)"
signalAddressRegex=r"si_addr\s+=\s+(0x[a-f\d]+)"
# errNoRegex=r"si_errno\s+=\s+(\d+)"

class LastEventAnalyzer:
    def __init__(self) -> None:
        self.ThreadID=None
        self.ThreadPID=None
        self.ThreadGID=None
        self.SignalNumber=None
        self.SignalAddress=None
        self.SignalErrorNumber=None
        self.SignalDescription=None  
        pass

    """This function gives signal address and signal code (not supported in aarch64) """
    def GetSignalAddressandErrorNo(self,corefilePath,executablePath,sharedLibPath):
        # print("IN last event...",sharedLibPath)
        p1=subprocess.Popen(["gdb-multiarch"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p1.stdin.write(('set sysroot '+SYS_ROOT+'\n').encode())
        p1.stdin.write(('set solib-search-path '+sharedLibPath+' \n').encode())
        p1.stdin.write(('file "'+executablePath+'"\n').encode())
        p1.stdin.write(('core-file '+corefilePath+'\n').encode())
        p1.stdin.write(('p $_siginfo \n').encode())
        p1.stdin.close()

        signalAddress=None
        errNo=None

        while True:
            line=p1.stdout.readline()
            if not line:
                break
            try:
                    line=line.decode()
            except:
                pass
            else:
                if re.search(signalAddressRegex,line):
                    x=re.search(signalAddressRegex,line)
                    signalAddress=x.group(1)
                # if re.search(errNoRegex,line):
                #     x=re.search(errNoRegex,line)
                #     errNo=x.group(1)
        
        if not signalAddress or not errNo:
            return "Unknown Address","Unknown Error"

        if signalAddress=="0x0":
            signalAddress+="(NULL)"
        return signalAddress,errNo

    """This function maps the signal number to the corresponding signal code"""
    def SignalNoToCode(self,SignalNumber):
        # print("Signal Number = ",SignalNumber)
        NumToCode={}
        NumToCode[1]="SIGHUP";
        NumToCode[2]="SIGINT";
        NumToCode[3]="SIGQUIT";
        NumToCode[4]="SIGILL";
        NumToCode[5]="SIGTRAP";
        NumToCode[6]="SIGABRT";
        NumToCode[7]="SIGBUS";
        NumToCode[8]="SIGFPE";
        NumToCode[9]="SIGKILL";
        NumToCode[10]= "SIGUSR1";
        NumToCode[11]= "SIGSEGV";
        NumToCode[12]= "SIGUSR2";
        NumToCode[13]= "SIGPIPE";
        NumToCode[14]= "SIGALRM";
        NumToCode[15]= "SIGTERM";
        NumToCode[16]= "SIGSTKFLT";
        NumToCode[17]= "SIGCHLD";
        NumToCode[18]= "SIGCONT";
        NumToCode[19]= "SIGSTOP";
        NumToCode[20]= "SIGTSTP";
        NumToCode[21]= "SIGTTIN";
        NumToCode[22]= "SIGTTOU";
        NumToCode[23]= "SIGURG";
        NumToCode[24]= "SIGXCPU";
        NumToCode[25]= "SIGXFSZ";
        NumToCode[26]= "SIGVTALRM";
        NumToCode[27]= "SIGPROF";
        NumToCode[28]= "SIGWINCH";
        NumToCode[29]= "SIGIO";
        NumToCode[30]= "SIGPWR";
        NumToCode[31]= "SIGSYS";
        
        
        SignalCode=NumToCode[SignalNumber]

        if not SignalCode:
            SignalCode="Unknown Signal"

        return SignalCode
        
    """
        This function helps in analysis of last event

        First it calls eu-redelf to read about the signal information sent by last thread, 
        which gives us the SignalCode, Thread's GID, and ErrorNumber

        Then we get the signal address from GDB (for this purpose we use siginfo structure, which is not supported while analysing aarch64 coredump)

        Finally we map the signal no. to the standard signal code, like SIGKILL, SIGSEGV, etc
        and create a description for last event.
        
    """
    def AnalyzeLastEvent(self,coreFilePath,executablePath,sharedLibPath,activeThreadId,activeThreadPID,Result):
        self.ThreadID=activeThreadId
        self.ThreadPID=activeThreadPID

        p1= subprocess.Popen(['eu-readelf --notes  "'+coreFilePath+'" | grep -B 4  "pid: '+activeThreadPID+'"'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)


        err=[]

        while True:
            line= p1.stderr.readline()
            if not line:
                break
            if line.strip()=="":
                continue
            if re.match("warning:",line):
                logwarning(line,Result.ResultPath)
                continue
            try:
                line=line.decode()
            except:
                pass
            else:
                if line.count("raise.c")>0 or line.count("No such file or directory")>0:
                    continue
                err.append(line)

        if len(err)>0:
            logerr("Error while reading Last event:\n",Result.ResultPath)
            for er in err:
                logerr(er,Result.ResultPath)
        while True:
            line = p1.stdout.readline()
            if not line:
                break
            try:
                line=line.decode()
            except:
                pass
            else:
                if re.search(sigInfoRegex,line):
                    x=re.search(sigInfoRegex,line)
                    self.SignalNumber=int(x.group(1))
                if re.search(pgrpInfoRegex,line):
                    x=re.search(pgrpInfoRegex,line)
                    self.ThreadGID=int(x.group(1))
                if re.search(ErroNoRegex,line):
                    x=re.search(ErroNoRegex,line)
                    self.SignalErrorNumber=int(x.group(1))

        errorno,signalAddress = self.GetSignalAddressandErrorNo(coreFilePath,executablePath,sharedLibPath)

        description= self.SignalNoToCode(self.SignalNumber)

        if self.SignalNumber==11:
            description+=": Invalid memory reference to address "+signalAddress
        elif self.SignalNumber==4 or self.SignalNumber==8:
            description+=": Faulty Instruction at address "+signalAddress
        else:
            description+=": (Error Number "+str(self.SignalErrorNumber)+")"

        self.SignalAddress=signalAddress
        self.SignalDescription=description



            
        
        
