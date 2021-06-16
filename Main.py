import sys,getopt,os
import pathlib
from pprint import pprint

from GetMainExecutable import GetMainExecutable
from SharedLibAnalyzer import SharedLibAnalyzer
from UnwindAnalyzer import UnwindAnalyzer
from AnalysisResult import Result


class CoreDumpAnalysis:
    def __init__(self):
        self.Result=Result()
        pass

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
        if(len(dirs)!=3):
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

    def analyze(self,argv):
        DirectoryPath=''
        try:
            opts,args = getopt.getopt(argv,"d:")
        except getopt.GetoptError:
            print ('Wrong Input Format')
            print ('Usage: file.py -d <directory name>')
            return
        flg=0;
        for opt,arg in opts:
            if opt=='-d':
                flg=1
                DirectoryPath=arg
        if flg==0:
            print('Directory path not  specified')
            return
        if os.path.exists(DirectoryPath) and os.path.isdir(DirectoryPath):
            directory= self.Get_Dir_Structure(DirectoryPath)
            if(directory==None):
                print("Invalid Directory Structure")
                return 
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

            print('\nExtracting Main Exectuable...')
            GetMainExecutable().Analyze(self.Result)

            print('\nRetrieving Shared Libraries...')
            SharedLibAnalyzer().Analyze(self.Result)

            # pprint(self.Result.__dict__)

            print('\nUnwiding Stacktraces...')
            UnwindAnalyzer().Analyze(self.Result)

            # self.Result.printResult()

                

            


        else:
            print ('Invalid Directory Path')
            sys.exit(2)



if __name__ == "__main__":
    CoreDumpAnalyzerObj=CoreDumpAnalysis()
    CoreDumpAnalyzerObj.analyze(sys.argv[1:])


