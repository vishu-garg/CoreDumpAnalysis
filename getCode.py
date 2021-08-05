from config import SYS_ROOT
import math
import subprocess
from Logs import getWarningLogger,getConsoleLogger,logconsole,getErrLogger,logerr,logwarning
class GetCode:
    def __init__(self) -> None:

        pass



    def analyze(self,Result):
        """
        This function is used to find the code snippet which has caused the error
        Parameters:
        Result:The result in which we have to save it
        Returns:
        None(Just save the code snippet and error line in Result object)
        """
        
        self.coreFilePath=Result.coreDumpInfo['FilePath']
        self.executablePath=Result.ExecutablePath
        self.SharedLibPath=Result.directoryInfo["SharedLibPath"]
        
        codeFilePath=Result.codeFilePath
        StackFrames=Result.Threads[0].StackFrames
        num=len(StackFrames)
        if codeFilePath is None:
            codeFilePath=Result.directoryInfo['CodeFilePath']
        prev_frame=None
        line=None
        prev_cpp=None
        first=False

        # We are finding the top most stack trace which is present in the project but the exception is 
        # for infinite recursion because there the stack trace below is causing the error

        for i in range(num):
            if StackFrames[i].Info['File'] is not None and StackFrames[i].Info['Line'] is not None: 
                frame=StackFrames[i].Info['Function'].split('+')[0]
                cppFile=StackFrames[i].Info['File']
                if prev_frame is None and (cppFile.count(codeFilePath)>0):
                    prev_cpp=StackFrames[i].Info['File']
                    line=StackFrames[i].Info['Line']
                    prev_frame=frame
                    first=True

                elif prev_frame ==  frame and prev_cpp==cppFile:
                    line=StackFrames[i].Info['Line']
                    break
                elif first:
                    break



        #this approach uses gdb-multiarch  

        # p1=subprocess.Popen(["gdb-multiarch"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        # p1.stdin.write(('set sysroot '+SYS_ROOT+'\n').encode())
        # p1.stdin.write(('set solib-search-path '+self.SharedLibPath+' \n').encode())
        # p1.stdin.write(('file "'+self.executablePath+'"\n').encode())
        # p1.stdin.write(('core-file '+self.coreFilePath+'\n').encode())  
        # p1.stdin.write(('echo --> Code Begins\n').encode())   
        # p1.stdin.write(('list '+prev_cpp+": "+line+'\n').encode())   
        # p1.stdin.write(('echo --> Code Ends\n').encode())
        # p1.stdin.write('quit \n'.encode())
        # p1.stdin.close()
        # ans_arr=p1.stdout.readlines()

        #here we use read the file approach 
        if line is not None:    
            logconsole(str(line+"  "+prev_frame+"  "+prev_cpp),Result.ResultPath)  
            try:
                #here the file is read but if we have to 
                # find the code from some online source have to use some approach
                f=open(prev_cpp,"r")
                lines=f.readlines()
                codeSnippet=""
                line=int(line)
                low=max(0,(line-4))
                high=min(len(lines),(line+5))

                #here we are finding the errorLine 
                Result.errorLine=lines[line-1]

                # codeSnippet="".join(lines[low:high])

                for i in range(low,high):
                    if i==(line-1):
                        #this is done so that bold could be done in frontend
                        codeSnippet+="<b>"+lines[i][0:-1]+"</b>"+'\n'
                    else:
                        codeSnippet+=lines[i]
                #print(codeSnippet)
                logconsole(codeSnippet,Result.ResultPath)   
                Result.codeSnippet=codeSnippet
            except Exception as e:
            
                logerr("Code File Not Found",Result.ResultPath)   
                logerr(e,Result.ResultPath) 
        else:
            logerr("Code Not Found",Result.ResultPath)
       
        
