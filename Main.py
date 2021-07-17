from logging import log
from ErrorLog import logErr,setErrLogger
from WarningLog import logWarning,setWarningLogger
from ConsoleLogs import logConsole,setConsoleLogger
import sys,getopt,os
import pathlib
import json
from pprint import pprint

from GetMainExecutable import GetMainExecutable
from SharedLibAnalyzer import SharedLibAnalyzer
from UnwindAnalyzer import UnwindAnalyzer
from AnalysisResult import Result


class CoreDumpAnalysis:
    def __init__(self):
        self.Result=Result()
        setErrLogger(self.Result.ResultPath)
        setWarningLogger(self.Result.ResultPath)
        setConsoleLogger(self.Result.ResultPath)
        pass

    def isCallbyCMD(self):
        return self.callByCMD

    def getResultIdandPath(self):
        return self.Result.ResultID,self.Result.ResultPath


    """This function gives information about the coredump file"""
    def generateCoreDumpFileInfo(self,path):
        data = {}
        data['FilePath']=path
        data['FileName']=os.path.basename(path)
        data['FileSize']=os.path.getsize(path)
        return data

    def Get_CoreDump_File(self,DirectoryPath):
        dirs= os.listdir(DirectoryPath)
        cnt=0
        coreFilePath=""
        for file in dirs:
            filePath = os.path.join(DirectoryPath,file)
            if(os.path.isfile(filePath)):
                fileExtension= pathlib.Path(filePath).suffix
                if(fileExtension==".core"):
                    cnt=cnt+1
                    coreFilePath=filePath
        if(cnt==0):
            print('CoreFile not found.')
            sys.exit(2)
        elif(cnt>1):
            print('Multiple CoreFiles present. (Invalid)')
            sys.exit(2)
        else:
            return self.generateCoreDumpFileInfo(coreFilePath)
        
    """This function checks the directory structure, and returns the paths,if OK else returns None"""
    def Get_Dir_Structure(self,DirPath):
        dirs = os.listdir(DirPath)
        if(len(dirs)<3):
            return
        else:
            HasCoreFile=False
            HasSummaryFile=False
            HasSharedLibDir=False

            data={}
        
            for file in dirs:
                filePath= os.path.join(DirPath,file)
                if(os.path.isdir(filePath)):
                    dirName=os.path.basename(filePath)
                    if(dirName=="sharedlib"):
                        HasSharedLibDir=True
                        data['SharedLibPath']=filePath
                else:
                    fileName=os.path.basename(filePath)
                    if(fileName=="summary.txt"):
                        HasSummaryFile=True
                        data['SummaryFilePath']=filePath
                    else:
                        fileExtension= pathlib.Path(filePath).suffix
                        if(fileExtension==".core"):
                            HasCoreFile=True
                            data['CoreFilePath']=filePath
            
            if HasCoreFile and HasSharedLibDir and HasSummaryFile :
                return data

    """ 
        This function is the entry point of the whole anlaysis

        Params: (argv: The path/argument for the directory path, callByCMD: True in case if request is coming from shell)

        Response: The response contains the resultID on successful analysis, ontherwise contains the path to erros.log file, which
                    contains the errors, as they are logged.
    """
    def analyze(self,argv,callByCMD):
        self.callByCMD=callByCMD
        
        #if call is by a CMD then extract path from arguments
        if callByCMD:
            DirectoryPath=''
            try:
                opts,args = getopt.getopt(argv,"d:")
            except getopt.GetoptError:
                # print ('Wrong Input Format')
                # print ('Usage: file.py -d <directory path>')
                logErr('Wrong Input Format')
                logErr('Usage: file.py -d <directory path>')
                logErr('Wrong Input Format')
                sys.exit(2)
            flg=0;
            for opt,arg in opts:
                if opt=='-d':
                    flg=1
                    DirectoryPath=arg
            if flg==0:
                # print('Directory path not  specified')
                # print ('Usage: file.py -d <directory path>')
                logErr('Directory path not  specified')
                sys.exit(2)
        else:
            #We already have the direcotry path in this case
            DirectoryPath=argv

        #validate the directory path    
        if os.path.exists(DirectoryPath) and os.path.isdir(DirectoryPath):
            #get directory's structure
            directory= self.Get_Dir_Structure(DirectoryPath)
            if(directory==None):
                # print("Invalid Directory Structure")
                logErr("Invalid Directory Structure")
                sys.exit(2) 
            coredump=self.generateCoreDumpFileInfo(directory['CoreFilePath'])

            #Store the necessary info about input files
            self.Result.directoryInfo=directory
            self.Result.directoryPath=DirectoryPath
            self.Result.coreDumpInfo=coredump

            """After uploads and validations we start the analysis work"""

            #Gives us the path of the executable file from summary.txt
            logConsole('Extracting Main Exectuable...\n')
            # print('\nExtracting Main Exectuable...')
            GetMainExecutable().Analyze(self.Result)

            #Retrieving of shared libraries 
            logConsole('Retrieving Shared Libraries...\n')
            # print('\nRetrieving Shared Libraries...')
            SharedLibAnalyzer().Analyze(self.Result)

            #Getting information about the threads and stacktraces
            logConsole('Unwiding Stacktraces...\n')
            # print('\nUnwiding Stacktraces...')
            UnwindAnalyzer().Analyze(self.Result)

            
            #Convert the result in JSON format
            jsondata=json.dumps(self.Result.__dict__,default=lambda o: o.__dict__, indent=4)
            # print(jsondata)

            #store the result
            self.Result.StoreResult(jsondata)

            #if the call is not by shell, then retun resultID and status code
            if not callByCMD:
                return self.Result.ResultID, 201
            else:
                logConsole("Analysis Complete...")
                logConsole("Result is stored at "+self.Result.ResultPath)
                if callByCMD:
                    print("Analysis Complete...")
                    print("Result is stored at "+self.Result.ResultPath)
            
        else:
            logErr('Invalid Directory Path')
            print ('Invalid Directory Path')
            sys.exit(2)



if __name__ == "__main__":
    CoreDumpAnalyzerObj=CoreDumpAnalysis()
    try:
        CoreDumpAnalyzerObj.analyze(sys.argv[1:],True)
    except SystemExit:
        logConsole("Some Error Occurred, Exiting...")
        resultId,resultPath=CoreDumpAnalyzerObj.getResultIdandPath()
        print("Logs can be viewed at :",resultPath)


