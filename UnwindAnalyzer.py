from Logs import getWarningLogger,getConsoleLogger,logconsole,getErrLogger,logerr,logwarning
from os import system
from re import sub
import re
import sys
from pprint import pprint
import subprocess


from SystemContext import SystemContext
from StackFrame import StackFrame
from Thread import Thread
from LastEventAnalyzer import LastEventAnalyzer
from config import SYS_ROOT 


regex=r"\s*(\w+):\s+(.+)"
addrToStringRegex=r'.*:\s+"(.+)"'
# threadInfoRegex=r"(\*)?\s+(\d+)\s+Thread\s+0x[\da-f]+\s+\(LWP\s+(\d+)\).*"
threadInfoRegex=r"(\*)?\s+(\d+)\s+(?:Thread\s+0x[a-f\d]+\s+)?\(?LWP\s+(\d+)\)?\s+.*"
registerValRegex=r".*\s*\$(\d+)\s+=\s+.*\s?0?x?[a-f\d]+.*"

MAX_FRAMES=32

class UnwindAnalyzer :
    def __init__(self) -> None:
        self.systemContext = SystemContext()
        self.Result=None
        pass

    """
        This function extracts AUXV info from notes of Core-Dump file
        It uses the eu-readelf command for that purpose.
    """
    def getAuxvFromNotes(self,corefilePath):
        
        #to store the shell output
        output=[]

        #spawn the subprocess
        p1 = subprocess.Popen(["eu-readelf","--note",corefilePath],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        
        #reading the output
        flg=0
        while True:
            line = p1.stdout.readline()
            try:
                line=line.decode()
            except:
                pass
            else:
                if not line:
                    break
                if "CORE" in line and flg==1:
                    break
                elif flg==1:
                    line.strip()
                    output.append(line)
                elif "AUXV" in line:
                    flg=1
                else:
                    continue
        return output

    """
        This function helps in mapping output in a key-value pair in dictionary
    """
    def getFields(self,auxvInfoOutput):
        fields={}
        for line in auxvInfoOutput:
            x= re.search(regex,line)
            if x:
                key=x.group(1)
                val=x.group(2)
                fields[key]=val
        return fields

    """
        This function provide information on a particular address (extracted from notes)
        It uses x/s 0x00000(address) command of GDB
    """
    def getStringfromAddr(self,addr):
        
        #starting subprocess
        p1=subprocess.Popen(["gdb-multiarch"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p1.stdin.write(('set sysroot '+SYS_ROOT+'\n').encode())
        p1.stdin.write(('set solib-search-path '+self.SharedLibPath+' \n').encode())
        p1.stdin.write(('file "'+self.executablePath+'"\n').encode())
        p1.stdin.write(('core-file '+self.coreFilePath+'\n').encode())
        p1.stdin.write(('x/s '+addr+'\n').encode())
        p1.stdin.close()
        
        #reading if any errors
        err=[]
        while True:
            line= p1.stderr.readline()
            if not line:
                break
            try:
                line=line.decode()
            except:
                pass
            else:
                if line.strip()=="":
                    continue
                if re.match("warning:",line):
                    logwarning(line,self.Result.ResultPath)
                    continue
                if line.count("raise.c")>0 or line.count("No such file or directory")>0:
                    continue;
                err.append(line)

        if len(err)>0:
            logerr("Error while getting AUXV fields information at address: "+addr+"\n",self.Result.ResultPath)
            for er in err:
                logerr(er,self.Result.ResultPath)

        #reading output
        output=None
        while True:
            line= p1.stdout.readline()
            if line:
                try:
                    line=line.decode()
                except:
                    pass
                else:
                    if addr in line:
                        output=line
            else:   
                break

        x1= re.search(addrToStringRegex,output)
        if x1:
            x=x1.group(1)
            return x
        return "None"

    """
        This function is responsible for extracting and storing 
        system info from AUXV note of corefile

        It makes 2 function calls,
        1) First it calls getAuxvFromNotes() function which gives the information about system context
        2) Then getFields() function is called which parses the values present in the note in a dictionary

        The few fields information is stored in an address which can be extracted using gdb, for this purpose we called getStringfromAddr() function

        Finally we store the results in a variable called systemContext 
    """
    def setAuxvFields(self,Result):
        corefilePath=Result.coreDumpInfo['FilePath']
        
        #extracting AUXV info from corefile
        auxvInfoOutput=self.getAuxvFromNotes(corefilePath)

        #parsing AUXV notes fields in a 'fields' dictionary
        fields=self.getFields(auxvInfoOutput)

        #setting results
        self.systemContext.UID=int(fields['UID'])
        self.systemContext.EUID=int(fields['EUID'])
        self.systemContext.GID=int(fields['GID'])
        self.systemContext.EGID=int(fields['EGID'])
        self.systemContext.PageSize=int(fields['PAGESZ'])
        self.systemContext.EntryPoint=hex(int(fields['ENTRY'],16))
        self.systemContext.BasePlatform=self.getStringfromAddr(fields['BASE'])
        self.systemContext.SystemArchitecture=self.getStringfromAddr(fields['PLATFORM'])
        

    """ 
        This function stores the information
        about different system parameters like,

        1) Sytem_Arch.
        2) Entry Point Address
        3) Page/Frame Size of process

        and many more

        It calls the setAuxvFields function which parses the AUXV note present in corefile and set key-value pairs for the desired information.
    """
    def setContextFields(self,Result):
        
        #These are default values
        self.systemContext.ProcessArchitecture= "N/A"
        self.systemContext.SystemUpTime="Could not be obtained"

        #AUXV note contains system information about this process
        self.setAuxvFields(Result)

        #store the result
        Result.systemContext=self.systemContext

    """
        This function helps in getting information (ID and PID) about the number of threads running in our process
        Along with this we are also able to get info about the last active thread

        The commands we used are => info threads (which lists up all the threads in our process)
    """
    def getThreads(self):
        
        #start the subprocess and insert commands 
        p1=subprocess.Popen(["gdb-multiarch"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p1.stdin.write(('set sysroot '+SYS_ROOT+'\n').encode())
        p1.stdin.write(('set solib-search-path '+self.SharedLibPath+' \n').encode())
        p1.stdin.write(('file "'+self.executablePath+'"\n').encode())
        p1.stdin.write(('core-file '+self.coreFilePath+'\n').encode())
        p1.stdin.write(('echo --> ThreadBegins\n').encode())
        p1.stdin.write(('info threads\n').encode())
        p1.stdin.write(('echo --> ThreadEnds\n').encode())
        p1.stdin.close()
        
        #cnt variable gives the count of all the threads
        #activeThreadId and activeThreadPIDs are use to store info about the last active thread
        #ThreadIdsandPIDs stores thread IDs and PIDs
        cnt=0
        flg=0
        activeThreadId=None
        activeThreadPID=None
        ThreadIdsandPIDs=[]

        #reading output
        while True:
            line=p1.stdout.readline()
            if line:
                try:
                    line=line.decode()
                except:
                    pass
                else:
                    if line.count("ThreadEnds") >0 or line.count("(Exiting)") or flg==2:
                        flg=2
                        continue
                    if flg==1:
                        if re.match(threadInfoRegex,line) :
                            x=re.match(threadInfoRegex,line)
                            cnt+=1
                            threadIDandPID=[]
                            threadId=x.group(2)
                            threadPID=x.group(3)
                            threadIDandPID.append(threadId)
                            threadIDandPID.append(threadPID)
                            ThreadIdsandPIDs.append(threadIDandPID)
                            isActive=x.group(1)
                            if isActive:
                                activeThreadId=threadId
                                activeThreadPID=threadPID
                    elif line.count("ThreadBegins") >0:
                        flg=1
                    else:
                        continue
            else:
                break

        #finally returning result
        return cnt,ThreadIdsandPIDs,activeThreadId,activeThreadPID

    """
        The function uses "bt" command to parse the information about the number of frames in this thread
    """
    def getFrameNum(self,id):
        
        #starting subprocess and calling the command
        p1=subprocess.Popen(["gdb-multiarch"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p1.stdin.write(('set sysroot '+SYS_ROOT+'\n').encode())
        p1.stdin.write(('set solib-search-path '+self.SharedLibPath+' \n').encode())
        p1.stdin.write(('file "'+self.executablePath+'"\n').encode())
        p1.stdin.write(('core-file '+self.coreFilePath+'\n').encode())
        p1.stdin.write(('thread '+str(id)+'\n').encode())
        p1.stdin.write(('echo ---BackTracingThread--- \n').encode())
        p1.stdin.write(('bt \n').encode())
        p1.stdin.write(('echo ---BackTracingThreadEnd--- \n').encode())
        p1.stdin.close()
        flg=0
        
        #cnt will give us the count of number of frames
        cnt=0
        while True:
            line= p1.stdout.readline()
            if line:
                try:
                    line=line.decode()
                except:
                    pass
                else:
                    if line.count("---BackTracingThreadEnd---")>0 or flg==2 or cnt>=MAX_FRAMES:
                        p1.terminate()
                        flg=2
                        break
                    if flg==1 and re.search(r"#(\d*)",line):
                        cnt+=1
                    elif line.count("---BackTracingThread---")>0:
                        flg=1
                        if re.search(r"#(\d*)",line):
                            cnt+=1
                    else:
                        continue
            else:
                break

        #return the count of frames
        return cnt


    """"
        This function analyses the cur stackframes,
        It returns an array where each element is containing a stackFrame object 

        For each stackFrame we get followinfg information from this function:
        1) BP = base pointer / frame pointer (in aarch64) 
        2) IP = instruction pointer / program counter (in aarch64)
        3) SP = stack pointer 
    """
    def AnalyzeCurFrames(self,ThreadId, frames):
        
        #array to store result
        StackFrames=[]

        #start subprocess
        p1=subprocess.Popen(["gdb-multiarch"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p1.stdin.write(('set sysroot '+SYS_ROOT+'\n').encode())
        p1.stdin.write(('set solib-search-path '+self.SharedLibPath+' \n').encode())
        p1.stdin.write(('file "'+self.executablePath+'"\n').encode())
        p1.stdin.write(('core-file '+self.coreFilePath+'\n').encode())
        p1.stdin.write(('thread '+str(ThreadId)+'\n').encode())
        for frameNum in range (0,frames):
            p1.stdin.write(('frame '+str(frameNum)+'\n').encode())
            p1.stdin.write(('p $pc \n').encode())
            p1.stdin.write(('p $x29 \n').encode())
            p1.stdin.write(('p $sp \n').encode())
        p1.stdin.close()
        
        stackFrame = StackFrame()
        stackFrame.threadId=ThreadId
        
        frameCnt=0
        #read output
        while True:
            line= p1.stdout.readline()
            # print(line)
            if not line:
                break
            try:
                line=line.decode()
            except:
                pass
            else:
                if re.match(registerValRegex,line):
                    x=re.match(registerValRegex,line)
                    num_id=x.group(1)
                    num_id=str((int)(num_id)%3)
                    if num_id=='1':
                        x1= re.match(r".*\s*\$(\d+)\s+=\s+.*\s+(0?x?[a-f\d]+)\s+.*",line)
                        num_val=x1.group(2)
                        stackFrame.IP=num_val
                    elif num_id=='2':
                        x1=re.search(r".*\s*\$(\d+)\s+=\s+(.*)",line)
                        BP_in_Int=int(x1.group(2))
                        stackFrame.BP=hex(BP_in_Int)
                    elif num_id=='0':
                        x1= re.match(r".*\s*\$(\d+)\s+=\s+.*\s+(0?x?[a-f\d]+)\s+.*",line)
                        num_val=x1.group(2)
                        stackFrame.SP=num_val

                        frameNum=frameCnt
                        stackFrame.FrameNo=frameNum;
                        StackFrames.append(stackFrame)
                        frameCnt+=1
                        stackFrame=StackFrame()
                        stackFrame.threadId=ThreadId

        return StackFrames

    """
        This function helps in getting line information from 
        instruction pointer address.
    """
    def getLineFromIP(self,StackFrames):
        p1=subprocess.Popen(["gdb-multiarch"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p1.stdin.write(('set sysroot '+SYS_ROOT+'\n').encode())
        p1.stdin.write(('set solib-search-path '+self.SharedLibPath+' \n').encode())
        p1.stdin.write(('file "'+self.executablePath+'"\n').encode())
        p1.stdin.write(('core-file '+self.coreFilePath+'\n').encode())
        
        for stackFrame in StackFrames:
            p1.stdin.write(('info line *'+str(stackFrame.IP)+'\n').encode())
        
        p1.stdin.write(('quit \n').encode())
        p1.stdin.close()

        err=[]

        while True:
            line=p1.stderr.readline()
            if not line:
                break;
            try:
                line=line.decode()
            except:
                pass
            else:
                if line.strip()=="":
                    continue
                if re.match("warning:",line):
                    logwarning(line,self.Result.ResultPath)
                    continue
                if line.count("raise.c")>0 or line.count("No such file or directory")>0:
                    break
                err.append(line)

        if len(err)>0:
            logerr("Error extracting Stacktrace....",self.Result.ResultPath)
            for er in err:
                logerr(er,self.Result.ResultPath)

        flg=0
        output=""

        cnt=0

        while True:
            line= p1.stdout.readline()
            if not line:
                break
            try:
                line=line.decode()
            except:
                pass
            else:
                if flg==1 and line.count("(gdb)")>0:
                    flg=0
                    if len(output)>0:
                        extractInfoRegEx= r'Line\s+(\d+)\s+of\s+"(.*)".*<(.+).*>'

                    x=re.match(extractInfoRegEx,output)

                    if x:

                        LineNum=x.group(1)
                        FileName=x.group(2)
                        FunctionName=x.group(3)

                        StackFrames[cnt].Info["Line"]=LineNum
                        StackFrames[cnt].Info["File"]=FileName
                        if(FunctionName.find("+")>=0):
                            FunctionName=FunctionName.split('+')
                            FunctionName=FunctionName[0]
                        StackFrames[cnt].Info["Function"]=FunctionName

                    output=""
                    cnt+=1

                if flg==1:
                    output+=line.strip()
                elif re.search(r"Line\s+",line) or re.search(r"No line",line):
                    flg=1
                    x= re.match(r"\(gdb\)\s+(.*)",line).group(1)
                    output+=x.strip()
                else:
                    continue
        
    """
        This function helps in getting information about the stacktrace
        of this thread.

        It calls 3 functions as described below-
        1) getFrameNum = to get the number of frames
        2) AnalyseCurFrames= to get the information about the frames in this thread
        3) getLineFromIP = to get the info about last executed line (pc) of the frames 
    """
    def UnwindCurrentThread(self,ThreadId):
        numFrames=self.getFrameNum(ThreadId)
        StackFrames=self.AnalyzeCurFrames(ThreadId,numFrames)
        self.getLineFromIP(StackFrames)
        return StackFrames


    """
        This is the entry function of UnwindAnlyser class

        It provides us information about the following:
        1) System Information
        2) Threads Infomation
        3) Stackframes Information
        4) Last Event Analysis
    """
    def Analyze(self,Result):
        self.Result=Result

        #set file paths needed during analysis
        self.coreFilePath=Result.coreDumpInfo['FilePath']
        self.executablePath=Result.ExecutablePath
        self.SharedLibPath=Result.directoryInfo["SharedLibPath"]
        
        # Context Fields contains system information
        self.setContextFields(Result)

        # Unwind Thread Information
        numThreads, ThreadIdsandPIDs, activeThreadId, activeThreadPID=self.getThreads()

        # print("Found ",numThreads," threads....")
        logconsole("Found "+str(numThreads)+" threads....",Result.ResultPath)
        
        #Store the info about the threads
        Threads=[]
        for threadId,threadPID in ThreadIdsandPIDs:
            print("Analyzing Thread No.",threadId)
            logconsole("Analyzing Thread No."+str(threadId),Result.ResultPath)
            stackTraces= self.UnwindCurrentThread(threadId)
            thread = Thread()
            thread.Id=threadId
            thread.PID=threadPID
            thread.StackFrames=stackTraces
            Threads.append(thread)
        Result.Threads= Threads

        # Analyze Last Event
        print("Analyzing Last Event...")
        logconsole("Analyzing Last Event...",Result.ResultPath)
        lastEvent=LastEventAnalyzer()
        lastEvent.AnalyzeLastEvent(self.coreFilePath,self.executablePath,self.SharedLibPath,activeThreadId,activeThreadPID,Result)
        Result.LastEvent=lastEvent
        


        