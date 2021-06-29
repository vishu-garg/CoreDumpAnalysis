import pickle 
import pandas as pd
from levenshtein_distUtil import levenshtein_distUtil
from KNNUtil import KNNUtil
class Cluster:
    def __init__(self) -> None:
        self.X_train= pd.DataFrame(columns=['StackFrames', 'SignalDescription', 'SystemArch','CreationDate'])
        self.knnUtilObj=KNNUtil()
        self.levenshtein_distUtilObj=levenshtein_distUtil()
        self.lcp=None
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
      return temp

    def fit(self,df):
        self.X_train=self.X_train.append(df);
        data=df['StackFrames'].split(" ")
        response=self.knnUtilObj.remove_equals(data)
        text=" ".join(response)
        self.knnUtilObj.N=self.knnUtilObj.N+1;
        for word in set(text.split(' ')):
            if word not in self.knnUtilObj.word2idx:
                self.knnUtilObj.word2idx[word] = len(self.knnUtilObj.word2idx)
                self.knnUtilObj.doc_freq.append(0)
            self.knnUtilObj.doc_freq[self.knnUtilObj.word2idx[word]] += 1

        prv_lcp = self.lcp
        if not self.lcp:
          self.lcp=" ".join(response)
        else:
          arr_lcp=self.lcp.split(" ")
          temp_lcp=self.compute_lcp(arr_lcp,response)
          if (len(temp_lcp)!=len(response)):
            self.lcp=" ".join(temp_lcp)
        
        
        cur_lcp = self.lcp
        return

    def compute_scores(self,anchor_row):
        anchor_seq= anchor_row.split(" ")
        anchor_seq=self.knnUtilObj.remove_equals(anchor_seq)
        anchor_weights=self.knnUtilObj.weights(anchor_seq,0.5,7,15)
        scores=[]
        cntr=0

        for _, row in self.X_train.iterrows():
            stack_row=row["StackFrames"]
            stack_seq=stack_row.split(" ")
            stack_seq=self.knnUtilObj.remove_equals(stack_seq)

            stack_weights=self.knnUtilObj.weights(stack_seq,0.5,7,15)

            max_dist=sum(anchor_weights)+sum(stack_weights)
            dist=self.levenshtein_distUtilObj.calculate_dist(anchor_seq,anchor_weights,stack_seq,stack_weights)

            score = 0 if max_dist == 0 else 1 - dist / max_dist
            scores.append((score,cntr))
            cntr+=1
        scores.sort(reverse=True)
        return scores

    def GetNeighbours(self,anchor_row,k):
        scores=self.compute_scores(anchor_row)
        ans=[]
        k=min(k,len(scores))
        for i in range(k):
            ans.append(scores[i][1])

        return ans

    def predict(self,row):
        answers=[]
        nearest_neighbours=self.GetNeighbours(row["StackFrames"],5)
        return nearest_neighbours