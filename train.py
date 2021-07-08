import pandas as pd
from Clustering_Train import Clustering_Train
import pickle
def train(path="./dataset.csv"):
    """ This function is used to train the model with the given dataset
     
      Parameters:
      path (str): path of dataset

      Returns:
      None
        
    """
    chunk = pd.read_csv(path, chunksize=1000000,header=0)
    df = pd.concat(chunk)
    MainObj=Clustering_Train()
    MainObj.fit_dataset(df)
    print("done")
    file_pi = open('model.obj', 'wb') 
    pickle.dump(MainObj, file_pi)
    print("Saved")

if __name__ == '__main__':
    train()    