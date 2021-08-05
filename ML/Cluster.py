import pandas as pd
from levenshtein_distUtil import levenshtein_distUtil
from ClusteringUtil import ClusteringUtil
class Cluster:
    """ This is the class whose objects will be used as clusters in our model
    It stores 
    X_train: the training dataset in it for using KNN modelling
    ClusteringUtilObj: which has all the important information i.e. Size of X_train, frequency count of every frame in X_train
    levenshtein_distUtilObj: which is required to calculate Levenshtein distance
    lcp: Longest Common Prefix of the stack frames present in X_train which act as signature for every cluster object

    """
    def __init__(self) -> None:
        """This constructor is used to create the objects of ClusteringUtil and levenshtein_distUtil classes
         and also initaializing the X_train as a pandas.Dataframe and lcp as none

        Parameters:
        None

        Returns:
        None
        
        """   
        self.X_train= pd.DataFrame(columns=['StackFrames', 'SignalDescription', 'SystemArch','CreationDate'])
        self.ClusteringUtilObj=ClusteringUtil()
        self.levenshtein_distUtilObj=levenshtein_distUtil()
        self.lcp=None
        pass

    def fit(self,df):
        """ This function is used to fit the given list into the cluster i.e.
           * Adding the list to the X_train
           * Changing thr doc_frequency and value of N based on the new list
           * Modigying the LCP 

            Parameters:
            df(list): New Training value to be used for training the dataset

            Returns:
            None        
        
        """
        self.X_train=self.X_train.append(df);
        data=df['StackFrames'].split(" ")
        response=self.ClusteringUtilObj.remove_equals(data)
        text=" ".join(response)
        self.ClusteringUtilObj.N=self.ClusteringUtilObj.N+1;
        for word in set(text.split(' ')):
            if word not in self.ClusteringUtilObj.word2idx:
                self.ClusteringUtilObj.word2idx[word] = len(self.ClusteringUtilObj.word2idx)
                self.ClusteringUtilObj.doc_freq.append(0)
            self.ClusteringUtilObj.doc_freq[self.ClusteringUtilObj.word2idx[word]] += 1

        #prv_lcp = self.lcp
        if not self.lcp:
          self.lcp=" ".join(response)
        else:
          arr_lcp=self.lcp.split(" ")
          temp_lcp=self.ClusteringUtilObj.compute_lcp(arr_lcp,response)
          if (len(temp_lcp)!=len(response)):
            self.lcp=" ".join(temp_lcp)
        
        
        cur_lcp = self.lcp
        return

    def compute_scores(self,anchor_row):
        """This function is used to find the score for given stack traces with all 
           the stack traces present in X_train using  Levenshtein Distance based upon tf-idf concept
           and after that normalizing it

            Parameters:
            anchor_row(list): the stack trace for which we have to compute scores

            Returns:
            list: reversly sorted list having score and index of the stack traces in X_train with it          
        
        """
        anchor_seq= anchor_row.split(" ")
        anchor_seq=self.ClusteringUtilObj.remove_equals(anchor_seq)
        anchor_weights=self.ClusteringUtilObj.weights(anchor_seq,0.5,7,15) #finds weights based upon tf-idf concept 
                                                                            #keeping alpha=0.5,beta=7 and gamma=15
        scores=[]
        cntr=0
        
        #iterate over complete X_train and find the score for each stack Frames in it with the anchor_row
        for _, row in self.X_train.iterrows():
            stack_row=row["StackFrames"]
            stack_seq=stack_row.split(" ")
            stack_seq=self.ClusteringUtilObj.remove_equals(stack_seq)

            stack_weights=self.ClusteringUtilObj.weights(stack_seq,0.5,7,15)

            max_dist=sum(anchor_weights)+sum(stack_weights)
            dist=self.levenshtein_distUtilObj.calculate_dist(anchor_seq,anchor_weights,stack_seq,stack_weights)

            score = 0 if max_dist == 0 else 1 - dist / max_dist  #normalizing the value
            scores.append((score,cntr))
            cntr+=1
        scores.sort(reverse=True)
        return scores


    def predict(self,row,k=5):
      
        """ This function us used to find the most similar k stack traces index for the given 
         stack_frame(row).
         

          Parameters:
            row(list): the value for  which we have to find the similar stack traces. It should contain "StackFrames" value in it
            k(int): How many similar stack traces required
          Returns:
            list:return the list containing the index of k similar stacktraces present in X_train       
        
        """  
        anchor_row=row["StackFrames"]
        scores=self.compute_scores(anchor_row)
        ans=[]
        k=min(k,len(scores))
        for i in range(k):
            ans.append(scores[i][1])

        return ans