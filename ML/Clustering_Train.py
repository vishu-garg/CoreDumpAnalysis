from levenshtein_distUtil import levenshtein_distUtil
from KNNUtil import KNNUtil
from Cluster import Cluster
import pandas as pd
from sklearn.model_selection import train_test_split

class Clustering_Train:
  def __init__(self):
    self.Cluster_Signatures=KNNUtil()
    self.distUtil=levenshtein_distUtil()
    self.clusters=[]
    pass

  def compute_lcp(self,s,t):
    temp=[]
    len1=len(s)
    len2=len(t)
    length=min(len1,len2)
    for i in range(length):
      if(s[i]!=t[i]):
        break
      temp.append(s[i])
    return len(temp)

  def remove_equals(self,words):
        res = []
        for i, w in enumerate(words):
            if (i == 0 or words[i - 1] != w) and w.strip() != '':
                res.append(w)
        return res


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
    stackTrace=row['StackFrames'].split(" ")
    stackTrace=self.remove_equals(stackTrace)
    
    self.Cluster_Signatures.N=self.Cluster_Signatures.N+1;

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
      cur_lcp=self.compute_lcp(stackTrace,cur_stackTrace)
      
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
    for _,row in X_train.iterrows():
      self.fit_stack(row)

    print(len(self.clusters))

  def find_cluster(self,anchor_row):
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
      cluster_ind=self.find_cluster(row['StackFrames'])
      print(cluster_ind)
      single_val=[]
      ans=MainObj.clusters[cluster_ind].predict(row)
      for ind in ans:
          stackFrame=(self.clusters[cluster_ind].X_train.iloc[ind]["StackFrames"]).split(" ")
          val=MainObj.remove_equals(stackFrame)
          str_val=" ".join(val)
          print(str_val)
          single_val.append(str_val)
      return single_val

  def predict(self,X_test):
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
    ans=MainObj.predict(X_test)
    print(ans)