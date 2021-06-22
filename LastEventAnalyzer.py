import re
import subprocess
from ErrorLog import logErr
import sys
sigInfoRegex= r"info.si_signo:\s+(\d+)"
pgrpInfoRegex= r"pgrp:\s+(\d+)"
signalAddressRegex=r"si_addr\s+=\s+(0x[a-f\d]+)"
errNoRegex=r"si_errno\s+=\s+(\d+)"

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


    def GetSignalAddressandErrorNo(self,corefilePath,executablePath):
        p1=subprocess.Popen(["gdb"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p1.stdin.write(('file '+executablePath+'\n').encode())
        p1.stdin.write(('core-file '+corefilePath+'\n').encode())
        p1.stdin.write(('p $_siginfo \n').encode())
        p1.stdin.close()

        signalAddress=None
        errNo=None

        while True:
            line=p1.stdout.readline()
            if not line:
                break
            line=line.decode()
            if re.search(signalAddressRegex,line):
                x=re.search(signalAddressRegex,line)
                signalAddress=x.group(1)
            if re.search(errNoRegex,line):
                x=re.search(errNoRegex,line)
                errNo=x.group(1)
        
        if signalAddress=="0x0":
            signalAddress+="(NULL)"
        return signalAddress,errNo

    def SignalNoToCode(self,SignalNumber):
        # print("Signal Number = ",SignalNumber)
        NumToCode={}
        NumToCode[1]="SIGHUP";
        NumToCode[2]="SIGINT";
        NumToCode[3]="SIGQUIT";
        NumToCode[4]="SIGILL";
        NumToCode[6]="SIGABRT";
        NumToCode[7]="SIGBUS";
        NumToCode[8]="SIGFPE";
        NumToCode[9]="SIGKILL";
        NumToCode[11]= "SIGSEGV";
        NumToCode[13]= "SIGPIPE";
        NumToCode[14]= "SIGALRM";
        NumToCode[15]= "SIGTERM";
        NumToCode[10]= "SIGUSR1";
        NumToCode[12]= "SIGUSR2";
        NumToCode[17]= "SIGCHLD";
        NumToCode[18]= "SIGCONT";
        NumToCode[19]= "SIGSTOP";
        NumToCode[20]= "SIGTSTP";
        NumToCode[21]= "SIGTTIN";
        NumToCode[22]= "SIGTTOU";
        NumToCode[27]= "SIGPROF";
        NumToCode[31]= "SIGSYS";
        NumToCode[5]="SIGTRAP";
        NumToCode[23]= "SIGURG";
        NumToCode[26]= "SIGVTALRM";
        NumToCode[24]= "SIGXCPU";
        NumToCode[25]= "SIGXFSZ";
        NumToCode[16]= "SIGSTKFLT";
        NumToCode[29]= "SIGIO";
        NumToCode[30]= "SIGPWR";
        NumToCode[28]= "SIGWINCH";
        
        SignalCode=NumToCode[SignalNumber]

        if not SignalCode:
            SignalCode="Unknown Signal"

        return SignalCode
        

    def AnalyzeLastEvent(self,coreFilePath,executablePath,activeThreadId,activeThreadPID):
        self.ThreadID=activeThreadId
        self.ThreadPID=activeThreadPID

        try:
            p1= subprocess.Popen(['eu-readelf --notes  "'+coreFilePath+'" | grep -B 4  "pid: '+activeThreadPID+'"'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        except Exception as e:
            print(e.args[1])
            logErr(e.args[1])
            sys.exit(2)
        else:

            err=[]

            while True:
                line= p1.stderr.readline()
                if not line:
                    break
                line=line.decode()
                if line.count("raise.c")>0:
                    continue
                err.append(line)

            if len(err)>0:
                print("Error while reading Last event:\n")
                logErr("Error while reading Last event:\n")
                for er in err:
                    print(er)
                    logErr(er)
                sys.exit()
            while True:
                line = p1.stdout.readline()
                if not line:
                    break
                line=line.decode()
                if re.search(sigInfoRegex,line):
                    x=re.search(sigInfoRegex,line)
                    self.SignalNumber=int(x.group(1))
                if re.search(pgrpInfoRegex,line):
                    x=re.search(pgrpInfoRegex,line)
                    self.ThreadGID=int(x.group(1))

            signalAddress, ErrorNo= self.GetSignalAddressandErrorNo(coreFilePath,executablePath)

            description= self.SignalNoToCode(self.SignalNumber)

            if self.SignalNumber==11:
                description+=": Invalid memory reference to address "+signalAddress
            elif self.SignalNumber==4 or self.SignalNumber==8:
                description+=": Faulty Instruction at address "+signalAddress
            else:
                description+=": (Error Number "+ErrorNo+")"

            self.SignalAddress=signalAddress
            self.SignalDescription=description
            self.SignalErrorNumber=ErrorNo



            
        
        
