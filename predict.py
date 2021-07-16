from config import ScriptDir
import pickle
def predict(df):
     """
     This function is used to predict from the ml model and return the 5 resultIds which are closest to the given dataframe.
     Parameters:
      df (list):The dataframe for which we have to predict It should consists of StackFrames and SignalNumber

      Returns:
      list: the list having StackFrames,SignalNumber,SignalDescription, SystemArchitecture,creationDate,ResultId

     """
     filehandler= open(ScriptDir+"/model.obj", 'rb') 
     object = pickle.load(filehandler)
     ans=object.predict(df)
     #print(ans)
     return ans
 