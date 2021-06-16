class CD_Module :
    def __init__(self) -> None:
        self.StartAddr=None
        self.EndAddr=None
        self.FilePath=None
        self.LocalPath=None
        self.FileName=None
        self.FileSize=None
        pass
    def generateModule(self,StartAddr,EndAddr,FilePath,FileName,LocalPath,FileSize):
        self.StartAddr=StartAddr
        self.EndAddr=EndAddr
        self.FilePath=FilePath
        self.LocalPath=LocalPath
        self.FileName=FileName
        self.FileSize=FileSize

    def printModule(self):
        print(self.FileName)
        print(self.FilePath,": ",self.FileSize," bytes.")
        print("Stored Locally at ",self.LocalPath)
        print("Address: ",hex(self.StartAddr)," - ",hex(self.EndAddr),'\n')

    
