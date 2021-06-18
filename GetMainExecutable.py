import re,os,sys


execPathRegex=r"executablePath:\s(.*)"

class GetMainExecutable:
    def __init__(self) -> None:
        pass
    def Analyze(self,Result):
        SummaryFilePath = Result.directoryInfo['SummaryFilePath']
        with open(SummaryFilePath) as file:
            line=file.readline()
            x=re.search(execPathRegex,line)
            if x:
                ExecutablePath=x.group(1)
                if  os.path.exists(ExecutablePath) and os.path.isfile(ExecutablePath):
                    print("Executable Path: ",ExecutablePath)
                    Result.ExecutablePath=ExecutablePath
                else:
                    print("Err: Executable Path Not valid")
                    sys.exit(2)
            else:
                print("No match found [Make sure executable file path is given]")
                sys.exit(2)
