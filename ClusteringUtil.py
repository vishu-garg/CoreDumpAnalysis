import numpy as np
import math
from collections import Counter

class ClusteringUtil:
    """ 
    This class is the utility created for the both types of clusters i.e. ClusterOfCoredumps and ClusterofErrors class 
    It stores the
    N: signifies the number of dataset values the object has
    doc_freq:list having the frequency of all the functions present in the object
    word2idx: the dict which stores the index of every function/string in doc_freq i.e. using this we convert word to index
    """


    def __init__(self) -> None:
        """ This is used to initialize 
        N =0 :signifying that it has 0 values in it
        doc_freq:as empty list
        word2idx: as empty dict
        """
        self.N=0
        self.word2idx={}
        self.doc_freq=[]
        pass
    
    def remove_equals(self,words):
        """ This function removes the same adjacent stack frames that are same 
        (Basically used for removing the recursions present in the stack frame)
        Parameters:
        words (list) : stackframes list having the adjacent same values(Recursion)
        
        Returns:
        list: returns list having no adjacent same values present in the stack frame
        
        """
        res = []
        for i, w in enumerate(words):
            if (i == 0 or words[i - 1] != w) and w.strip() != '':
                res.append(w)
        return res

    

    def transform(self,words):
        """ This function gives the tf and idf value to each frame present in
        the words and returns the dict with frame name as key and value as tf,idf

        words (list) : stackframes list for which tf-idf value is required
        
        Returns:
        dict: returns dict having frame name as key and value as tf,idf
        
        """

        vec = {}
        words_freqs = Counter(words)
        for word, freq in words_freqs.items():
            if word not in self.word2idx or self.doc_freq[self.word2idx[word]]==0: 
                if self.N==0:
                  idf=0
                else:  
                 idf = np.log(self.N)
            else:
                idf = self.doc_freq[self.word2idx[word]]
            tf = np.sqrt(words_freqs[word])
            vec[word] = tf, idf  
        return vec


    def compute_lcp(self,s,t):
      """ This function computes the length of LCP(Longest Common Prefix) of two stack traces 
   
    Parameters:
    s (list): Stack trace 1
    t (list): Stack trace 2
    
    Returns:
    int: length of lcp of the two stack traces
    
     """
      temp=[]
      len1=len(s)
      len2=len(t)
      length=min(len1,len2)
      for i in range(length):
        if(s[i]!=t[i]):
          break
        temp.append(s[i])
      return temp

    
    def weights(self,coded_seq, alpha: float, beta: float, gamma: float):
        """ This function returns the weights given to each frame in coded_seq based 
        upon tf-idf concept. Here tf is refered as local weight which is calculated as:
          
          1/(1+i)^alpha where i refers to index of frame in the coded_seq

          and idf is global weight which is calculated as 

          1/(1+e^(-beta*(frequency of given frame in training dataset) -gamma)))

       Paramteres:

        coded_seq (list) : stackframes list for which tf-weights value is required
        alpha (float), beta (float), gamma (float):hyperparameters are used to tune smooth filtering
        
        Returns:
        list: returns list having weights for the given coded_seq
        
        """

        local_weight = [1 / (1 + i) ** alpha for i, _ in enumerate(coded_seq)]
        idfs =self.transform(coded_seq)
        global_weight = []
        for word in coded_seq:
            _, idf = idfs.get(word, (0, 0))
            score = idf
            global_weight.append(1 / (1 + math.exp(-beta * (score - gamma))))

        return [lw * gw for lw, gw in zip(local_weight, global_weight)]
