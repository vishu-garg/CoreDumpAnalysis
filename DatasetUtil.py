import os 
import json
import csv
from typing import AnyStr
import requests
import time


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
            data1['ResultId']=resultId

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
        
        fileNum=860

        while fileNum<998:
            
            fileNum+=1
            print(fileNum)
            ExeFilePath=path+"outputs/"+'/'+str(fileNum)+'.out'
            coreFilePath=path+"cores/"+'/core_'+str(fileNum)+".core"

            if not os.path.exists(ExeFilePath) or not os.path.isfile(coreFilePath):
                continue
            
            
  
            if not os.path.isfile(ExeFilePath) or not os.path.isfile(coreFilePath):
                continue
            start=time.time()
            response = self.analyseResult(ExeFilePath,coreFilePath)
                   
            if not response:
                continue
            end=time.time()
            self.AddCSVObj.add(response)
            
            print(f"Runtime of the program is {end - start}")
            data1={}
            data1['ResultId']=response
            data1['Time']=(end-start)

            # print(data1)

            if not os.path.exists('./stats.csv'):
                data_file = open('stats.csv', 'w')
                csv_writer = csv.writer(data_file)
                header = data1.keys()
                csv_writer.writerow(header)
                csv_writer.writerow(data1.values())
                data_file.close()
            else :
                with open('stats.csv', 'a') as f_object:
                     writer_object = csv.writer(f_object)
                     writer_object.writerow(data1.values())
                     f_object.close() 

#resultid  time 



if __name__ == '__main__':
    AnalyseObj=Analyse()
    # AnalyseObj.analyseResult('/home/vishu/Desktop/Dataset/Segmentation Fault/1.out','/home/vishu/Desktop/Dataset/Segmentation Fault/core_1')
    AnalyseObj.directoryPath("/home/rohit/Desktop/CoreDumpAnalysis-master(2)/CoreDumpAnalysis-master/")
 