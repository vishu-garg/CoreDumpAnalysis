from config import ScriptDir
from math import sin
from typing import Text
from levenshtein_distUtil import calculate_dist
from ClusteringUtil import ClusteringUtil
from sklearn.model_selection import train_test_split
from ClusterOfCoredumps import ClusterOfCoredumps
import pandas as pd
from predict import predict

import pickle

class ClusterOfErrors:
  """ Thw objects of this class are used for storing clusters of all types of different error types
  On creating a object it will create a object of ClusteringUtil classes which will be used during training and testing
   and also initaializing the cluster list which stores all the objects of clusterofcoredumps

  """
  def __init__(self):
    """ This constructor is used to create the objects of ClusteringUtil 
    classes and also initaializing the cluster list which stores all the objects of clusterofcoredumps
  
     Parameters:
      None

      Returns:
       None
    """  
    self.Cluster_Signatures=ClusteringUtil()
    self.clusters=[]
    pass



  def fit(self,X_train):
    """ This function is used to fit the given training dataset X_train into the model.
    This function modifies the tf-idf based upon the new value added 
    Also finds a suitable cluster for the given trainign row 
    (i.e having cluster having lcp length>=20 with this entry's stack frame)
    If not present will create a new Cluster object for this entry and append it to the self.cluster list
    Parameters:
    row (list): Data entry used for training should have 'StackFrames' value in it

    Returns:
    None
    
    """

    stackTrace=X_train['StackFrames'].split(" ") #splits the stackframe string to the list
    stackTrace=self.Cluster_Signatures.remove_equals(stackTrace) #removes the recursion
    
    self.Cluster_Signatures.N=self.Cluster_Signatures.N+1; #adding 1 signifying that a new row has been added

    for word in set(stackTrace):
        if word not in self.Cluster_Signatures.word2idx:
            self.Cluster_Signatures.word2idx[word] = len(self.Cluster_Signatures.word2idx)
            self.Cluster_Signatures.doc_freq.append(0)
        self.Cluster_Signatures.doc_freq[self.Cluster_Signatures.word2idx[word]] += 1

    max_ind=-1
    max_val=-1

    ind=0

    for cur_cluster in self.clusters:
      cur_stackTrace=cur_cluster.lcp.split(" ")
      cur_lcp=self.Cluster_Signatures.compute_lcp(stackTrace,cur_stackTrace)
      cur_lcp=len(cur_lcp)
      if( max_val<cur_lcp):
        max_val=cur_lcp
        max_ind=ind

      ind+=1

    if(max_val<10 and max_val != len(stackTrace)):
      Obj=ClusterOfCoredumps()
      Obj.fit(X_train)
      self.clusters.append(Obj)
    else:
      self.clusters[max_ind].fit(X_train)

      
  

  def find_cluster(self,anchor_row):
    """ This function is used to find the best cluster for the given stack frame .
    This function will find the levenshtein distance based on tf-idf of this stack frame 
    with lcp of all the clusters present in the model and based on this will return 
    the index of best cluster.

    Parameters:
    anchor_row (list): stack frame list 

    Returns:
    int: Index of most suitable cluster for the given stack frame
    """
    anchor_seq= anchor_row.split(" ")
    anchor_seq=self.Cluster_Signatures.remove_equals(anchor_seq)
    anchor_weights=self.Cluster_Signatures.weights(anchor_seq,0.5,7,15)
    scores=[]
    cntr=0
    for cluster in self.clusters:
        stack_row=cluster.lcp
        stack_seq=stack_row.split(" ")
        stack_seq=self.Cluster_Signatures.remove_equals(stack_seq)

        stack_weights=self.Cluster_Signatures.weights(stack_seq,0.5,7,15)

        max_dist=sum(anchor_weights)+sum(stack_weights)
        dist=calculate_dist(anchor_seq,anchor_weights,stack_seq,stack_weights)

        score = 0 if max_dist == 0 else 1 - dist / max_dist
        scores.append((score,cntr))
        cntr+=1
    ans=[]
    scores.sort(reverse=True)
    maxi=min(len(scores),5)
    for i in range(maxi):
      ans.append(scores[i][1])
    return ans
    

  def predict(self,row):
      """ This function is used to find the most suitable 5 stackframes for the given row 
      
    Parameters:
    row (list): list for which we have to predict the most similar stack frames

    Returns:
    list: list of the 5 resultIds whose stack frames that are having highest similarity with the given stackframe 
      
      """
      cluster_ind=self.find_cluster(row['StackFrames']) #finds the best cluster index
      ans=[]
      for i in cluster_ind:
        tmp=self.clusters[i].predict(row) #finds the 5 stack frames that are having 
                                                      #highest similarity with the given stackframe in the given cluster                                           
        for j in tmp:
          vl=self.clusters[i].X_train.iloc[j]['ResultId'] 
          vl=(int)(vl)
          ans.append(vl)
          
          stackFrame=(self.clusters[i].X_train.iloc[j]["StackFrames"]).split(" ")
          str_val=" ".join(stackFrame)
          #print(j,"       ",str_val)
         # print("\n\n\n") 
          
          if(len(ans)>=5):
            break
        if len(ans)>=5:
          break             
         
      return ans
