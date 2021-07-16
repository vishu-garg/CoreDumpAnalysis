from WarningLog import logWarning
from ConsoleLogs import logConsole
from os import system
from re import sub
import re
import sys
from pprint import pprint
import subprocess

from ErrorLog import logErr
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
MAX_FRAMES=30

class UnwindAnalyzer :
    def __init__(self) -> None:
        self.systemContext = SystemContext()
        pass

    def getAuxvFromNotes(self,corefilePath):
        output=[]
        p1 = subprocess.Popen(["eu-readelf","--note",corefilePath],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
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

    def getFields(self,auxvInfoOutput):
        fields={}
        for line in auxvInfoOutput:
            x= re.search(regex,line)
            if x:
                key=x.group(1)
                val=x.group(2)
                fields[key]=val
        return fields

    def getStringfromAddr(self,addr):
        p1=subprocess.Popen(["gdb-multiarch"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p1.stdin.write(('set sysroot '+SYS_ROOT+'\n').encode())
        p1.stdin.write(('set solib-search-path '+self.SharedLibPath+' \n').encode())
        p1.stdin.write(('file "'+self.executablePath+'"\n').encode())
        p1.stdin.write(('core-file '+self.coreFilePath+'\n').encode())
        p1.stdin.write(('x/s '+addr+'\n').encode())
        p1.stdin.close()
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
                    logWarning(line)
                    continue
                if line.count("raise.c")>0 or line.count("No such file or directory")>0:
                    continue;
                err.append(line)

        if len(err)>0:
            logErr("Error while getting AUXV fields information at address: "+addr+"\n")
            for er in err:
                logErr(er)

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

    def setAuxvFields(self,Result):
        corefilePath=Result.coreDumpInfo['FilePath']
        auxvInfoOutput=self.getAuxvFromNotes(corefilePath)
        fields=self.getFields(auxvInfoOutput)
        self.systemContext.UID=int(fields['UID'])
        self.systemContext.EUID=int(fields['EUID'])
        self.systemContext.GID=int(fields['GID'])
        self.systemContext.EGID=int(fields['EGID'])
        self.systemContext.PageSize=int(fields['PAGESZ'])
        self.systemContext.EntryPoint=hex(int(fields['ENTRY'],16))
        self.systemContext.BasePlatform=self.getStringfromAddr(fields['BASE'])
        self.systemContext.SystemArchitecture=self.getStringfromAddr(fields['PLATFORM'])
        

    def setContextFields(self,Result):
        self.systemContext.ProcessArchitecture= "N/A"
        self.systemContext.SystemUpTime="Could not be obtained"
        self.setAuxvFields(Result)
        Result.systemContext=self.systemContext
        # pprint(self.systemContext.__dict__)

    def getThreads(self):
        p1=subprocess.Popen(["gdb-multiarch"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p1.stdin.write(('set sysroot '+SYS_ROOT+'\n').encode())
        p1.stdin.write(('set solib-search-path '+self.SharedLibPath+' \n').encode())
        p1.stdin.write(('file "'+self.executablePath+'"\n').encode())
        p1.stdin.write(('core-file '+self.coreFilePath+'\n').encode())
        p1.stdin.write(('echo --> ThreadBegins\n').encode())
        p1.stdin.write(('info threads\n').encode())
        p1.stdin.write(('echo --> ThreadEnds\n').encode())
        p1.stdin.close()
        cnt=0
        flg=0
        activeThreadId=None
        activeThreadPID=None
        ThreadIdsandPIDs=[]

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

        return cnt,ThreadIdsandPIDs,activeThreadId,activeThreadPID

    def getFrameNum(self,id):
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
        cnt=0
        while True:
            line= p1.stdout.readline()
            if line:
                try:
                    line=line.decode()
                except:
                    pass
                else:
                    if line.count("---BackTracingThreadEnd---")>0 or flg==2 or cnt>=32:
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
        return cnt

    def AnalyzeCurFrames(self,ThreadId, frames):
        StackFrames=[]
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

        while True:
            line= p1.stdout.readline()
            if not line:
                break;
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
                    logWarning(line)
                    continue
                if line.count("raise.c")>0 or line.count("No such file or directory")>0:
                    break
                err.append(line)

        if len(err)>0:
            logErr("Error extracting Stacktrace....")
            for er in err:
                logErr(er)

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
        

    def UnwindCurrentThread(self,ThreadId):
        numFrames=self.getFrameNum(ThreadId)
        StackFrames=self.AnalyzeCurFrames(ThreadId,numFrames)
        self.getLineFromIP(StackFrames)
        return StackFrames


    def Analyze(self,Result):
        self.coreFilePath=Result.coreDumpInfo['FilePath']
        self.executablePath=Result.ExecutablePath
        self.SharedLibPath=Result.directoryInfo["SharedLibPath"]
        
        # Setting Context Fields
        self.setContextFields(Result)

        # Unwind Thread Information
        numThreads, ThreadIdsandPIDs, activeThreadId, activeThreadPID=self.getThreads()

        # print("Found ",numThreads," threads....")
        logConsole("Found "+str(numThreads)+" threads....")
        
        Threads=[]

        for threadId,threadPID in ThreadIdsandPIDs:
            print("Analyzing Thread No.",threadId)
            logConsole("Analyzing Thread No."+str(threadId))
            stackTraces= self.UnwindCurrentThread(threadId)
            thread = Thread()
            thread.Id=threadId
            thread.PID=threadPID
            thread.StackFrames=stackTraces
            Threads.append(thread)

        Result.Threads= Threads

        # for thread in Threads:
        #     thread.printThreadInfo()

        # Analyze Last Event
        print("Analyzing Last Event...")
        logConsole("Analyzing Last Event...")
        lastEvent=LastEventAnalyzer()
        lastEvent.AnalyzeLastEvent(self.coreFilePath,self.executablePath,self.SharedLibPath,activeThreadId,activeThreadPID)
        Result.LastEvent=lastEvent
        


        