class SystemContext:
    def __init__(self) -> None:
        self.UID=None
        self.EUID=None
        self.GID=None
        self.EGID=None
        self.PageSize=None
        self.EntryPoint=None
        self.BasePlatform=None
        self.SystemArchitecture=None
        self.ProcessArchitecture=None
        self.SystemUpTime=None
        pass
    def printSystemContext(self):
        print("System Context = \n")
        print(self.UID)
        print(self.EUID)
        print(self.GID)
        print(self.EGID)
        print(self.PageSize)
        print(self.EntryPoint)
        print(self.BasePlatform)
        print(self.SystemArchitecture)
        print(self.ProcessArchitecture)
        print(self.SystemUpTime)