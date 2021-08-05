
from pprint import pprint
from re import sub
import sys
import re
import subprocess
from config import SYS_ROOT


class StackFrame:
    def __init__(self) -> None:
        self.threadId=None
        self.FrameNo=None
        self.IP= None
        self.BP= None
        self.SP= None
        self.Info= {"Line":None,"File":None,"Function":None}
        pass


    def printStackFrame(self):
        print("Thread: ",self.threadId)
        print("Frame: ",self.FrameNo)
        print("Instruction Pointer: ",self.IP)
        print("Base Pointer: ",self.BP)
        print("Stack Pointer: ",self.SP)    
        if self.Info["Line"] :
            print("At line ",self.Info["Line"]," in file ",self.Info["File"]," on function ",self.Info["Function"]," .")
        