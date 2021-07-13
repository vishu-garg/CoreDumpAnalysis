from config import ScriptDir
import pickle
import re
def predict(df):
     filehandler= open(ScriptDir+"/model.obj", 'rb') 
     object = pickle.load(filehandler)
     val={'StackFrames':df}
     ans=object.predict(val)
     #print(ans)
     return ans
 