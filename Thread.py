from StackFrame import StackFrame


class Thread:
    def __init__(self) -> None:
        self.Id=None
        self.PID=None
        self.StackFrames=[StackFrame()]
        pass

    def printThreadInfo(self):
        print("Thread ID: ",self.Id)
        print("Thread PID: ",self.PID)
        print("Number of StackFrames: ",len(self.StackFrames))
        for stackFrame in self.StackFrames:
            print("--------------")
            stackFrame.printStackFrame()