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

    def analyze(self,argv,callByCMD):
        self.callByCMD=callByCMD
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
            DirectoryPath=argv
        if os.path.exists(DirectoryPath) and os.path.isdir(DirectoryPath):
            directory= self.Get_Dir_Structure(DirectoryPath)
            if(directory==None):
                # print("Invalid Directory Structure")
                logErr("Invalid Directory Structure")
                sys.exit(2) 
            coredump=self.generateCoreDumpFileInfo(directory['CoreFilePath'])

            self.Result.directoryInfo=directory
            self.Result.directoryPath=DirectoryPath
            self.Result.coreDumpInfo=coredump

            # print('Directory Path: ')
            # print(self.Result.directoryPath)
            # print('Directory Info: ')
            # pprint(self.Result.directoryInfo)
            # print('CoreDump Info: ')
            # pprint(self.Result.coreDumpInfo)

            logConsole('Extracting Main Exectuable...\n')
            # print('\nExtracting Main Exectuable...')
            GetMainExecutable().Analyze(self.Result)

            logConsole('Retrieving Shared Libraries...\n')
            # print('\nRetrieving Shared Libraries...')
            SharedLibAnalyzer().Analyze(self.Result)

            # pprint(self.Result.__dict__)
            logConsole('Unwiding Stacktraces...\n')
            # print('\nUnwiding Stacktraces...')
            UnwindAnalyzer().Analyze(self.Result)

            # self.Result.printResult()

            jsondata=json.dumps(self.Result.__dict__,default=lambda o: o.__dict__, indent=4)
            # print(jsondata)

            self.Result.StoreResult(jsondata)

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


