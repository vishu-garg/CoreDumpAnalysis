import json
import os
import uuid
import datetime
from LastEventAnalyzer import LastEventAnalyzer
from Thread import Thread
from SystemContext import SystemContext
from CD_Module import CD_Module



class Result:
    def __init__(self) -> None:
        self.directoryPath=None
        self.directoryInfo={'CoreFilePath':None,'SharedLibPath':None,'SummaryFilePath':None}
        self.coreDumpInfo={'FileName':None,'FilePath':None,'FileSize':None}
        self.ExecutablePath=None
        self.Modules=[CD_Module()]
        self.systemContext=SystemContext()
        self.Threads=[Thread()]
        self.LastEvent=LastEventAnalyzer()
        self.creationDate=datetime.datetime.now().isoformat()
        # self.suggestions=[]


        # self.ResultID=uuid.uuid4().hex
        ScriptDir=os.path.dirname(os.path.realpath(__file__))
        self.ResultID=str(len(os.listdir(ScriptDir+"/Results/"))+1)
        self.ResultPath=ScriptDir+"/Results/"+str(self.ResultID)+"/"
        
        if not os.path.exists(ScriptDir+"/Results/"):
            os.mkdir(ScriptDir+"/Results/")
        os.mkdir(self.ResultPath)

        pass

    def printResult(self):
        print("\n\n\n\n\n")
        print("Result ID: ",self.ResultID)
        print("Result Path: ",self.ResultPath)
        print("================\n")

        print("Directory Path: ",self.directoryPath)
        print("Directory Info: \n")
        print("1)CoreFile= ",self.directoryInfo['CoreFilePath'])
        print("2)Shared Libraries= ",self.directoryInfo['SharedLibPath'])
        print("3)Summary File= ",self.directoryInfo['SummaryFilePath'])
        print("================\n")

        print("CoreDump File Info: \n")
        print("1)FileName= ",self.coreDumpInfo["FileName"])
        print("2)FilePath= ",self.coreDumpInfo["FilePath"])
        print("3)FileSize= ",self.coreDumpInfo["FileSize"]," bytes")
        print("================\n")

        print("Main Executable FilePath= ",self.ExecutablePath)
        print("================\n")

        print("Number of Shared Libraries: ",len(self.Modules))
        for module in self.Modules:
            module.printModule()
            print("*********\n")
        print("================\n")

        print("Number of Threads: ",len(self.Threads))
        for thread in self.Threads:
            thread.printThreadInfo()
            print("**********\n")
        print("================\n")

        print("Last-Event Information: ")
        print("Thread ID: ",self.LastEvent.ThreadID)
        print("Thread PID: ",self.LastEvent.ThreadPID)
        print("Thread GID: ",self.LastEvent.ThreadGID)
        print(self.LastEvent.SignalDescription)
        print("================\n")


    def StoreResult(self,jsondata):
        ResultFilePath=self.ResultPath+"Results.txt"
        Resultfile= open(ResultFilePath,"w+")
        Resultfile.write(jsondata)
        Resultfile.close()

        SuggestionFilePath=self.ResultPath+"Suggestions.txt"
        Suggestionfile= open(SuggestionFilePath,"w+")
        Suggestionfile.write(json.dumps({"suggestions":[]},default=lambda o: o.__dict__, indent=4))
        Suggestionfile.close()

        # print("Analysis Completed...")
        # print("Result is stored at: ",ResultFilePath)



    #     print("================\n")

    #     print("Directory Path: ",self.directoryPath)
    #     print("Directory Info: \n")
    #     print("1)CoreFile= ",self.directoryInfo['CoreFilePath'])
    #     print("2)Shared Libraries= ",self.directoryInfo['SharedLibPath'])
    #     print("3)Summary File= ",self.directoryInfo['SummaryFilePath'])
    #     print("================\n")

    #     print("CoreDump File Info: \n")
    #     print("1)FileName= ",self.coreDumpInfo["FileName"])
    #     print("2)FilePath= ",self.coreDumpInfo["FilePath"])
    #     print("3)FileSize= ",self.coreDumpInfo["FileSize"]," bytes")
    #     print("================\n")

    #     print("Main Executable FilePath= ",self.ExecutablePath)
    #     print("================\n")

    #     print("Number of Shared Libraries: ",len(self.Modules))
    #     for module in self.Modules:
    #         module.printModule()
    #         print("*********\n")
    #     print("================\n")

    #     print("Number of Threads: ",len(self.Threads))
    #     for thread in self.Threads:
    #         thread.printThreadInfo()
    #         print("**********\n")
    #     print("================\n")

    #     print("Last-Event Information: ")
    #     print("Thread ID: ",self.LastEvent.ThreadID)
    #     print("Thread PID: ",self.LastEvent.ThreadPID)
    #     print("Thread GID: ",self.LastEvent.ThreadGID)
    #     print(self.LastEvent.SignalDescription)
    #     print("================\n")


        

    

# {'ExecutablePath': '/home/vishu/Desktop/11.out',
#  'LastEvent': <LastEventAnalyzer.LastEventAnalyzer object at 0x7fd89b3ef518>,
#  'Modules': [<CD_Module.CD_Module object at 0x7fd89b3ef160>,
#              <CD_Module.CD_Module object at 0x7fd89b3ef1d0>,
#              <CD_Module.CD_Module object at 0x7fd89b3ef2e8>,
#              <CD_Module.CD_Module object at 0x7fd89b3ef240>,
#              <CD_Module.CD_Module object at 0x7fd89b3ef2b0>,
#              <CD_Module.CD_Module object at 0x7fd89b3ef320>],
#  'Threads': [<Thread.Thread object at 0x7fd89b3ef748>],
#  'coreDumpInfo': {'FileName': 'corefile.core',
#                   'FilePath': '/home/vishu/Desktop/Dir2/corefile.core',
#                   'FileSize': 42602496},
#  'directoryInfo': {'CoreFilePath': '/home/vishu/Desktop/Dir2/corefile.core',
#                    'SharedLibPath': '/home/vishu/Desktop/Dir2/sharedlib',
#                    'SummaryFilePath': '/home/vishu/Desktop/Dir2/summary.txt'},
#  'directoryPath': '/home/vishu/Desktop/Dir2/',
#  'systemContext': <SystemContext.SystemContext object at 0x7fd89b3e5e48>}