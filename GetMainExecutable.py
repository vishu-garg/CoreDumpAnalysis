from ConsoleLogs import logConsole
import re,os,sys


execPathRegex=r"executablePath:\s(.*)"


""" This functions gives us the executable file, at the path 
provided in summary.txt files, this will be useful in later versions, when we can fetch the
executable from server using URL provided."""
class GetMainExecutable:
    def __init__(self) -> None:
        pass
    def Analyze(self,Result):
        SummaryFilePath = Result.directoryInfo['SummaryFilePath']
        with open(SummaryFilePath) as file:
            line=file.readline()
            # print(line)
            x=re.search(execPathRegex,line)
            if x:
                ExecutablePath=x.group(1)
                # print(ExecutablePath)
                if  os.path.exists(ExecutablePath) and os.path.isfile(ExecutablePath):
                    # print("Executable Path: ",ExecutablePath)
                    logConsole("Executable Path: "+ExecutablePath+" \n")
                    Result.ExecutablePath=ExecutablePath
                else:
                    print("Err: Executable Path Not valid")
                    sys.exit(2)
            else:
                print("No match found [Make sure executable file path is given]")
                sys.exit(2)
