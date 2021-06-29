import math
import numpy as np
from collections import Counter

class KNNUtil:

    def __init__(self) -> None:
        self.N=0
        self.word2idx={}
        self.doc_freq=[]
        pass
    
    def remove_equals(self,words):
        res = []
        for i, w in enumerate(words):
            if (i == 0 or words[i - 1] != w) and w.strip() != '':
                res.append(w)
        return res

    

    def transform(self,words):
        vec = {}
        words_freqs = Counter(words)
        for word, freq in words_freqs.items():
            if word not in self.word2idx or self.doc_freq[self.word2idx[word]]==0:
                idf = np.log(self.N)
            else:
                idf = self.doc_freq[self.word2idx[word]]
            tf = np.sqrt(words_freqs[word])
            vec[word] = tf, idf  
        return vec

    def remove_frame(self,words):
      words_freqs = Counter(words)
      for word, freq in words_freqs.items():
        self.doc_freq[self.word2idx[word]]-=freq

    def weights(self,coded_seq, alpha: float, beta: float, gamma: float):
        local_weight = [1 / (1 + i) ** alpha for i, _ in enumerate(coded_seq)]
        idfs =self.transform(coded_seq)
        global_weight = []
        for word in coded_seq:
            tf, idf = idfs.get(word, (0, 0))
            score = idf
            global_weight.append(1 / (1 + math.exp(-beta * (score - gamma))))

        return [lw * gw for lw, gw in zip(local_weight, global_weight)]
