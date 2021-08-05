from ClusterofErrors import ClusterOfErrors
import pandas as pd
from config import ScriptDir
from sklearn.model_selection import train_test_split
import pickle
class ML_Model:
  """
  This class is the main class of the model 
  For creating a model you need to have the object of this class
  On creating a object it will create a list of ClusterOfErrors which will store the objects of 
  ClusterOfErrors in it for all the 32 different types of errors 
  """

  def __init__(self):
      self.cluters=[]
      for i in range(32):
          temp=ClusterOfErrors()
          self.cluters.append(temp)

  def fit_single(self,X_train):
      """
      This function fits the given dataset row in the cluster of given SignalNumber 
      
      Parameters:
      X_train (list): The  data to be fit in the model 
      Returns:
      None
      """
      self.cluters[X_train['SignalNumber']].fit(X_train) 


  def fit(self,X_train):
        """
        This function fits the given dataset in the model It will check the datatype of X_train and 
        if it is of dataframe then will iterate every row and call fit_single for its every row
        
        Parameters:
        X_train (list/dataframe): The  data to be fit in the model 
        Returns:
        None
        """
        if isinstance(X_train, pd.DataFrame):
            for _,row in X_train.iterrows(): 
                self.fit_single(row)     
        else:
                self.fit_single(X_train)         
  
  def predict_single(self,X_test):
      """
      This function predicts and return the list of 5 resultIds that are most similar to given row  
      
      Parameters:
      X_train (list): The  data to be fit in the model 
      Returns:
      list: The resultIds that are most similar to given row
      """
      return self.cluters[X_test['SignalNumber']].predict(X_test)
      
  def predict(self,X_test):
      """
        This function predicts for given dataset in the model It will check the datatype of X_test and 
        if it is of dataframe then will iterate every row and call predct_single for its every row
        
        Parameters:
        X_test (list/dataframe): The data for which we have to be predict 
        Returns:
        if X_test is list
        list: The resultIds that are most similar to given row
        if X_test is dataframe
        2D list:The resultIds that are most similar for every row
        """
      ans=[]
      if isinstance(X_test, pd.DataFrame):
            for _,row in X_test.iterrows(): 
                ans.append(self.predict_single(row))   
      else:
            return self.predict_single(X_test) 
      return ans      


    