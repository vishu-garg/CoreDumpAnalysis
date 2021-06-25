import os 
import json
import csv
from typing import AnyStr
import requests


class making_dataset:
    def __init__(self) -> None:
        pass
    def add(self,resultId):
        if not os.path.exists('./Results/'+resultId+'/Results.txt'):
            return None
        with open('./Results/'+resultId+'/Results.txt', 'r') as file:
            data = json.load(file)
            lastThreadId=int(data['LastEvent']['ThreadID'])
            StackFrames=data['Threads'][lastThreadId-1]['StackFrames']
            data1={}
            data1['StackFrames']=""
            for frame in StackFrames:
                str=frame["Info"]["Function"]
                if not str:
                    continue
                if len(data1['StackFrames'])>0:
                    data1['StackFrames']+=" "
                data1['StackFrames']+=str

            data1['SignalNumber']=data['LastEvent']['SignalNumber']
            data1['SignalDescription']=data['LastEvent']['SignalDescription']
            data1['SystemArch']=data['systemContext']['SystemArchitecture']
            data1['CreationDate']=data['creationDate']

            # print(data1)

            if not os.path.exists('./dataset.csv'):
                data_file = open('dataset.csv', 'w')
                csv_writer = csv.writer(data_file)
                header = data1.keys()
                csv_writer.writerow(header)
                csv_writer.writerow(data1.values())
                data_file.close()
            else :
                with open('dataset.csv', 'a') as f_object:
                     writer_object = csv.writer(f_object)
                     writer_object.writerow(data1.values())
                     f_object.close() 
class Analyse:
    def __init__(self) -> None:
        self.AddCSVObj=making_dataset()
        self.url='http://127.0.0.1:5000/analyse'
        pass

    def analyseResult(self,exePath,corefilePath):
        data={
            'corefilePath':corefilePath,
            'executablePath':exePath
        }

        # print(data)

        x = requests.post(self.url,json=data)
        
        if x.status_code >=400:
            print("Error")
            return
        
        response=x.json()

        return response['resultID']

    def directoryPath(self,path):
        if not os.path.exists(path):
            return
        
        fileNum=1

        while True:
            ExeFilePath=path+'/'+str(fileNum)+'.out'
            coreFilePath=path+'/core_'+str(fileNum)

            if not os.path.exists(ExeFilePath) or not os.path.isfile(coreFilePath):
                break
            
            fileNum+=1

            if not os.path.isfile(ExeFilePath) or not os.path.isfile(coreFilePath):
                continue

            response = self.analyseResult(ExeFilePath,coreFilePath)

            if not response:
                continue

            self.AddCSVObj.add(response)





if __name__ == '__main__':
    AnalyseObj=Analyse()
    # AnalyseObj.analyseResult('/home/vishu/Desktop/Dataset/Segmentation Fault/1.out','/home/vishu/Desktop/Dataset/Segmentation Fault/core_1')
    AnalyseObj.directoryPath("/home/vishu/Desktop/Dataset/Segmentation Fault")
    AnalyseObj.directoryPath("/home/vishu/Desktop/Dataset/Aborted Fault")
    AnalyseObj.directoryPath("/home/vishu/Desktop/Dataset/Arithmetic Exceptions")
    # making_datasetObj=making_dataset()
    # making_datasetObj.add("936da2a6d4614dd0a40ceb3a16e1ef1f")
