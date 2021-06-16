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


regex=r"\s*(\w+):\s+(.+)"
addrToStringRegex=r'.*:\s+"(.+)"'
# threadInfoRegex=r"(\*)?\s+(\d+)\s+Thread\s+0x[\da-f]+\s+\(LWP\s+(\d+)\).*"
threadInfoRegex=r"(\*)?\s+(\d+)\s+(?:Thread\s+0x[a-f\d]+\s+)?\(?LWP\s+(\d+)\)?\s+.*"
registerValRegex=r".*\s*\$(\d+)\s+=\s+.*\s+(0x[a-f\d]+).*"

class UnwindAnalyzer :
    def __init__(self) -> None:
        self.systemContext = SystemContext()
        pass

    def getAuxvFromNotes(self,corefilePath):
        output=[]
        p1 = subprocess.Popen(["eu-readelf","--notes",corefilePath],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        flg=0
        while True:
            line = p1.stdout.readline()
            line=line.decode()
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
        p1=subprocess.Popen(["gdb"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p1.stdin.write(('file '+self.executablePath+'\n').encode())
        p1.stdin.write(('core-file '+self.coreFilePath+'\n').encode())
        p1.stdin.write(('x/s '+addr+'\n').encode())
        p1.stdin.close()

        output=None

        while True:
            line= p1.stdout.readline()
            if line:
                line=line.decode()
                if addr in line:
                    output=line
            else:   
                break

        x= re.search(addrToStringRegex,output).group(1)
        return x

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
        p1=subprocess.Popen(["gdb"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p1.stdin.write(('file '+self.executablePath+'\n').encode())
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
                line= line.decode()
                if line.count("ThreadEnds") >0 or line.count("(Exiting)") or flg==2:
                    # print(line)
                    flg=2
                    continue
                if flg==1:
                    # print(line)
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
        p1=subprocess.Popen(["gdb"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p1.stdin.write(('file '+self.executablePath+'\n').encode())
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
                line=line.decode()
                if line.count("---BackTracingThreadEnd---")>0 or flg==2:
                    flg=2
                    continue
                if flg==1 and re.search(r"#(\d*)",line):
                    cnt+=1
                    # print(line)
                elif line.count("---BackTracingThread---")>0:
                    flg=1
                    if re.search(r"#(\d*)",line):
                        cnt+=1
                        # print(line)
                else:
                    continue
            else:
                break
        return cnt

    def AnalyzeCurFrame(self,ThreadId, frameNum):
        stackFrame = StackFrame()
        stackFrame.threadId=ThreadId
        stackFrame.FrameNo=frameNum
        p1=subprocess.Popen(["gdb"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p1.stdin.write(('file '+self.executablePath+'\n').encode())
        p1.stdin.write(('core-file '+self.coreFilePath+'\n').encode())
        p1.stdin.write(('thread '+str(ThreadId)+'\n').encode())
        p1.stdin.write(('frame '+str(frameNum)+'\n').encode())
        p1.stdin.write(('p $rip \n').encode())
        p1.stdin.write(('p $rbp \n').encode())
        p1.stdin.write(('p $rsp \n').encode())
        p1.stdin.close()
        while True:
            line= p1.stdout.readline()
            if not line:
                break;
            line= line.decode()
            if re.match(registerValRegex,line):
                x=re.match(registerValRegex,line)
                num_id=x.group(1)
                num_val=x.group(2)
                # print(num_id,num_val)
                if num_id=='1':
                    stackFrame.IP=num_val
                elif num_id=='2':
                    stackFrame.BP=num_val
                elif num_id=='3':
                    stackFrame.SP=num_val
        stackFrame.getLineFromIP(self.executablePath,self.coreFilePath)
        return stackFrame

    def UnwindCurrentThread(self,ThreadId):
        numFrames=self.getFrameNum(ThreadId)
        StackFrames=[]
        for frame in range(numFrames):
            CurTrace=self.AnalyzeCurFrame(ThreadId,frame)
            StackFrames.append(CurTrace)
        return StackFrames


    def Analyze(self,Result):
        self.coreFilePath=Result.coreDumpInfo['FilePath']
        self.executablePath=Result.ExecutablePath
        
        # Setting Context Fields
        self.setContextFields(Result)

        # Unwind Thread Information
        numThreads, ThreadIdsandPIDs, activeThreadId, activeThreadPID=self.getThreads()

        print("Found ",numThreads," threads....")
        
        Threads=[]

        for threadId,threadPID in ThreadIdsandPIDs:
            print("Analyzing Thread No.",threadId)
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
        lastEvent=LastEventAnalyzer()
        lastEvent.AnalyzeLastEvent(self.coreFilePath,self.executablePath,activeThreadId,activeThreadPID)
        Result.LastEvent=lastEvent
        


        