from config import ScriptDir
import json
import os 
import csv
import pickle
def updateUtil(resultId):
    """
     This function is used as a util for updating process . It will take the resultId and read the result.txt of that 
     and then make changes in dataset.csv and returns the data list having StackFrames,SignalNumber,SignalDescription,
     SystemArchitecture,creationDate,ResultId
     Parameters:
      resultId (str): The resultId whose data to be added in the model 

      Returns:
      list: the list having StackFrames,SignalNumber,SignalDescription, SystemArchitecture,creationDate,ErrorCode,ResultId

     """
    if not os.path.exists('./Results/'+resultId+'/Results.txt'):
        return None   
    #opens the result.txt     
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
        data1['ErrorCode']=data['errorLine']
        data1['ResultId']=int(resultId)
        # print(data1)

        #TODO
        # dataset.csv is updated here so we require locks also to avoid race condition
        if not os.path.exists('./dataset1.csv'):
            data_file = open('dataset1.csv', 'w')
            csv_writer = csv.writer(data_file)
            header = data1.keys()
            csv_writer.writerow(header)
            csv_writer.writerow(data1.values())
            data_file.close()
        else :
            with open('dataset1.csv', 'a') as f_object:
                writer_object = csv.writer(f_object)
                writer_object.writerow(data1.values())
                f_object.close() 
        return data1

def update(resultId):
     """
     This function is used to update the model. It will read the model.obj file and then update the model and then saves the changes
     
     Parameters:
      resultId (str): The resultId whose data to be added in the model 

      Returns:
      None

     """
     filehandler= open(ScriptDir+"/model.obj", 'rb') #reads the file
     object = pickle.load(filehandler)
     
     #this is done for batch learning because in batch learning the resultId will be the list containing more than one resultId     
     if isinstance(resultId, list):
         for result in resultId:
             data1=updateUtil(result)
             object.fit(data1)
            
     else :
         data1=updateUtil(resultId)
         object.fit(data1)
        #  print(data1)

     #TODO 
     # Here implementation of some types of locks should be done
     #  because writing could be invoked multiply so race condition can occur   
     filehandler=open(ScriptDir+"/model.obj",'wb')
     pickle.dump(object,filehandler)   
     #print("done") 
          