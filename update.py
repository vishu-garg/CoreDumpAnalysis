from config import ScriptDir
import json
import os 
import csv
import pickle
def updateUtil(resultId):
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
            #Loading the model from the saved file
        return data1

def update(resultId):
     filehandler= open(ScriptDir+"/model.obj", 'rb') 
     object = pickle.load(filehandler)
     if isinstance(resultId, list):
         for result in resultId:
             print("here")
             data1=updateUtil(result)
             object.fit_dataset(data1)
     else :
         data1=updateUtil(resultId)
         print("doing")   
         object.fit_dataset(data1)

       
     filehandler=open(ScriptDir+"/model.obj",'wb')
     pickle.dump(object,filehandler)   
     print("done") 
          