from levenshtein_distUtil import levenshtein_distUtil
from ClusteringUtil import ClusteringUtil
from Cluster import Cluster
import pandas as pd
from sklearn.model_selection import train_test_split
import pickle

class Clustering_Train:
  """ This class is the main class of the model 
  For creating a model you need to have the object of this class
  On creating a object it will create a object of ClusteringUtil and levenshtein_distUtil
  classes which will be used during training and testing

  """
  def __init__(self):
    """ This constructor is used to create the objects of ClusteringUtil and levenshtein_distUtil
  classes and also initaializing the cluster list
  
    Parameters:
    None

    Returns:
    None
    """  
    self.Cluster_Signatures=ClusteringUtil()
    self.distUtil=levenshtein_distUtil()
    self.clusters=[]
    pass



 # def tune_Signature(self,prv_lcp,cur_lcp):
 #       if prv_lcp and len(prv_lcp) == len(cur_lcp):
 #         return
 
 #       if prv_lcp != None:
 #         self.Cluster_Signatures.remove_frame(prv_lcp)
 #         self.Cluster_Signatures.N-=1

 #       data=cur_lcp
 #       response=self.Cluster_Signatures.remove_equals(data)
 #       text=" ".join(response)
 #       self.Cluster_Signatures.N=self.Cluster_Signatures.N+1;
 #       for word in set(text.split(' ')):
 #           if word not in self.Cluster_Signatures.word2idx:
 #               self.Cluster_Signatures.word2idx[word] = len(self.Cluster_Signatures.word2idx)
 #               self.Cluster_Signatures.doc_freq.append(0)
 #           self.Cluster_Signatures.doc_freq[self.Cluster_Signatures.word2idx[word]] += 1
 #       return

  def fit_stack(self,row):
    """ This function is used to fit the given training dataset row into the model.
    This function modifies the tf-idf based upon the new value added 
    Also finds a suitable cluster for the given trainign row 
    (i.e having cluster having lcp length>=20 with this entry's stack frame)
    If not present will create a new Cluster object for this entry and append it to the self.cluster list
    Parameters:
    row (list): Data entry used for training should have 'StackFrames' value in it

    Returns:
    None
    
    """
    stackTrace=row['StackFrames'].split(" ") #splits the stackframe string to the list
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

    if(max_val<20 and max_val != len(stackTrace)):
      Obj=Cluster()
      Obj.fit(row)
      self.clusters.append(Obj)
    else:
      self.clusters[max_ind].fit(row)

      
  def fit_dataset(self,X_train):
    """ This function is used to fit the given training dataset into the model.
    This function will call the function fit_stack for every entry present in the X_train

    Parameters:
    X_train (pandas.Dataframe): Training Dateset used to train the model

    Returns:
    None
    
    """
    for _,row in X_train.iterrows():
      self.fit_stack(row)

    #print(len(self.clusters))




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
        dist=self.distUtil.calculate_dist(anchor_seq,anchor_weights,stack_seq,stack_weights)

        score = 0 if max_dist == 0 else 1 - dist / max_dist
        scores.append((score,cntr))
        cntr+=1
    scores.sort(reverse=True)
    best_index=scores[0][1]
    return best_index
    

  def predict_single(self,row):
      """ This function is used to find the most suitable 5 stackframes for the given row 
      
    Parameters:
    row (list): list for which we have to predict the most similar stack frames

    Returns:
    list: list of the 5 stack frames that are having highest similarity with the given stackframe 
      
      """
      cluster_ind=self.find_cluster(row['StackFrames']) #finds the best cluster index
      print(cluster_ind)
      single_val=[]
      ans=self.clusters[cluster_ind].predict(row) #finds the 5 stack frames that are having 
                                                      #highest similarity with the given stackframe in the given cluster
      for ind in ans:
          stackFrame=(self.clusters[cluster_ind].X_train.iloc[ind]["StackFrames"]).split(" ")
          val=self.Cluster_Signatures.remove_equals(stackFrame)
          str_val=" ".join(val)
          print(str_val)
          single_val.append(str_val)
      return single_val

  def predict(self,X_test):
      """ This function is used to find the most suitable 5 stackframes for the given testing datset 
        
      Parameters:
      row (list): list for which we have to predict the most similar stack frames

      Returns:
      list: list of the 5 stack frames that are having highest similarity with the given stackframe 
        
        """

      value=[]
      if isinstance(X_test, pd.DataFrame):
        for _,row in X_test.iterrows(): 
          single_val=self.predict_single(row)
          value.append(single_val)         
      else:
          single_val=self.predict_single(X_test)
          value.append(single_val)
      return value;    

if __name__ == '__main__':
    chunk = pd.read_csv("C:/Users/Hp/Downloads/CoreDumpAnalysis-master/CoreDumpAnalysis-master/ML/temp_dataset.csv", chunksize=1000000,header=0)
    df = pd.concat(chunk)
    X_train, X_test = train_test_split(df, test_size=0.01, random_state=3)
    MainObj=Clustering_Train()
    MainObj.fit_dataset(df)
    
    #Saving the model as binary 
    file_pi = open('model.obj', 'wb') 
    pickle.dump(MainObj, file_pi)
    print("Saved")
    
    #Loading the model from the saved file

    filehandler= open("model.obj", 'rb') 
    object = pickle.load(filehandler)
    print("loaded")

    tmp={"StackFrames":"GitSnippetRepository.java GitSnippetRepository.java EclipseGitSnippetRepository.java Worker.java"}
    #predicting using the loaded model
    print(object.predict(tmp))