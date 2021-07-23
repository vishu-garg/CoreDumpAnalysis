from ML_Model import ML_Model
from config import ScriptDir
import pandas as pd
from ClusterofErrors import ClusterOfErrors
import pickle
def train(path=ScriptDir+"/dataset.csv"):
    """ This function is used to train the model with the given dataset
     
      Parameters:
      path (str): path of dataset

      Returns:
      None
        
    """
    chunk = pd.read_csv(path, chunksize=1000000,header=0)
    df = pd.concat(chunk)
    
    MainObj=ML_Model()
    MainObj.fit(df)
    file_pi = open(ScriptDir+"/model.obj", 'wb') 
    pickle.dump(MainObj, file_pi)
    print("Done Training")

if __name__ == '__main__':
    train()    