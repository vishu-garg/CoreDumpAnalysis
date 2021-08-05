from config import ScriptDir
from typing import Text
from MLUtility import distDiff, getErrorStr, remove_equals
from ClusterOfCoredumps import ClusterOfCoredumps

class ClusterOfErrors:
  """ The objects of this class are used for storing clusters of all types of different error types
  On creating a object it will initaialize the cluster list which stores all the objects of clusterofcoredumps
  """
  def __init__(self):
    """ This constructor is used to initaialize the cluster list which stores all the objects of clusterofcoredumps
  
    Parameters:
      None
    Returns:
       None
    """  
    self.clusters=[]
    pass

  

  def fit(self,X_train):
    """ This function is used to fit the given training dataset X_train into the model.    
    Also finds a suitable cluster for the given training row 
    (i.e having cluster with same type of errorCode)
    If not present will create a new Cluster object for this entry and append it to the self.cluster list
    Parameters:
    row (list): Data entry used for training should have 'StackFrames' value in it
    Returns:
    None
    
    """

    stackTrace=X_train['StackFrames'].split(" ") #splits the stackframe string to the list
    stackTrace=remove_equals(stackTrace) #removes the recursion
    
    max_ind=-1
    max_val=-1
    ind=0
    # print(X_train)
    pres_errorStr=getErrorStr(X_train['ErrorCode'])
    
    for cur_cluster in self.clusters:
      cur_str=cur_cluster.errorStr
      if(cur_str==pres_errorStr):
        max_ind=ind
        break
      ind+=1

    if max_ind==-1:
      Obj=ClusterOfCoredumps()
      Obj.fit(X_train)
      self.clusters.append(Obj)
    else:
      self.clusters[max_ind].fit(X_train)

      
  

  def find_cluster(self,pres_errorStr):
    """ This function is used to find the best cluster for the given stack frame .
    This function will find the edit distance of this errorCode with the errorCode of All Coredumps
    and based on this will return the index of best cluster.
    Parameters:
    anchor_row (list): data row
    Returns:
    int: Index of most suitable cluster for the given stack frame
    """
    
    ind=0
    best_ind=0
    similarity=-1 #Initializing with the minimum value

    #when a large dataset is present this approach can be used here we are finding five clusters instead of one
    
    # mp=[]
    # for cur_cluster in self.clusters:
    #   cur_str=cur_cluster.errorStr
    #   max_dist=len(cur_str)+len(pres_errorStr)

    #   cur_dist=distDiff(cur_str,pres_errorStr)
    #   cur_similarity = 0 if max_dist == 0 else 1 - cur_dist / max_dist 
    #   mp.append(cur_similarity,ind)
    #   ind+=1
    # mp.sort(reverse=True)  


    for cur_cluster in self.clusters:
      cur_str=cur_cluster.errorStr
      max_dist=len(cur_str)+len(pres_errorStr)

      cur_dist=distDiff(cur_str,pres_errorStr)
      cur_similarity = 0 if max_dist == 0 else 1 - cur_dist / max_dist 
      
      if cur_similarity>similarity:
        best_ind=ind
        similarity=cur_similarity
      ind+=1  
    return best_ind
    

  def predict(self,row,k=5):
      """ This function is used to find the most suitable 5 stackframes for the given row 
      
    Parameters:
    row (list): list for which we have to predict the most similar stack frames
    Returns:
    list: list of the 5 resultIds whose stack frames that are having highest similarity with the given stackframe 
      
      """
      # print(row)
      pres_errorStr=getErrorStr(row['ErrorCode'])
      ans=[]
      if(pres_errorStr==""):
        temp=[]
        l=len(self.clusters)
        for i in range(l):
          ans_arr=self.clusters[i].predict(row,k)
          for i in range(k):
           temp.append(ans_arr[i])
        temp.sort(reverse=True) 
        k=min(k,len(temp))
        for i in range(k):
          ans.append(temp[i][1])

      else:
        cluster_ind=self.find_cluster(pres_errorStr) #finds the best cluster index
        ans_arr=self.clusters[cluster_ind].predict(row,k)
        k=min(k,len(ans_arr))
        for i in range(k):
          ans.append(ans_arr[i][1])

      return ans
