from WarningLog import logWarning
from pprint import pprint
from re import sub
import sys
import re
import subprocess
from ErrorLog import logErr
from config import SYS_ROOT


class StackFrame:
    def __init__(self) -> None:
        self.threadId=None
        self.FrameNo=None
        self.IP= None
        self.BP= None
        self.SP= None
        self.Info= {"Line":None,"File":None,"Function":None}
        pass

    def getLineFromIP(self,executablePath,coreFilePath,sharedLibPath):
        # try:
        p1=subprocess.Popen(["gdb-multiarch"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        # except Exception as e:
        #     # print(e.args[1])
        #     logErr(e.args[1])
        #     sys.exit(2)
        # else:
        p1.stdin.write(('set sysroot '+SYS_ROOT+'\n').encode())
        p1.stdin.write(('set solib-search-path '+sharedLibPath+' \n').encode())
        p1.stdin.write(('file "'+executablePath+'"\n').encode())
        p1.stdin.write(('core-file '+coreFilePath+'\n').encode())
        p1.stdin.write(('info line *'+str(self.IP)+'\n').encode())
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
            # print("Error extracting Stacktrace....")
            logErr("Error extracting Stacktrace....")
            for er in err:
                # print(er)
                logErr(er)
            # sys.exit(2)

        flg=0
        output=""

        while True:
            line= p1.stdout.readline()
            if not line:
                break
            try:
                line=line.decode()
            except:
                pass
            else:
                # print(line)
                if flg==2:
                    continue
                if flg==1 and line.count("(gdb)")>0:
                    flg=2
                    continue

                if flg==1:
                    output+=line.strip()
                elif re.search(r"Line\s+",line):
                    flg=1
                    x= re.match(r"\(gdb\)\s+(.*)",line).group(1)
                    output+=x.strip()
                else:
                    continue

        if len(output)==0:
            # print("Frame is Empty")
            return

        extractInfoRegEx= r'Line\s+(\d+)\s+of\s+"(.*)".*<(.+).*>'

        x=re.match(extractInfoRegEx,output)

        LineNum=x.group(1)
        FileName=x.group(2)
        FunctionName=x.group(3)

        self.Info["Line"]=LineNum
        self.Info["File"]=FileName
        self.Info["Function"]=FunctionName

    def printStackFrame(self):
        print("Thread: ",self.threadId)
        print("Frame: ",self.FrameNo)
        print("Instruction Pointer: ",self.IP)
        print("Base Pointer: ",self.BP)
        print("Stack Pointer: ",self.SP)    
        if self.Info["Line"] :
            print("At line ",self.Info["Line"]," in file ",self.Info["File"]," on function ",self.Info["Function"]," .")
        