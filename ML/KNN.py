from levenshtein_distUtil import levenshtein_distUtil
from knnUtil import KNNUtil
import pandas as pd
from sklearn.model_selection import train_test_split

class KNN:
    def __init__(self) -> None:
        self.X_train=None
        self.knnUtilObj=KNNUtil()
        self.levenshtein_distUtilObj=levenshtein_distUtil()
        pass

    def fit(self,df):
        texts=[]
        self.X_train=df
        for index, row in self.X_train.iterrows():
            data=row['StackFrames'].split(" ")
            response=self.knnUtilObj.remove_equals(data)
            temp=" ".join(response)
            texts.append(temp)
            
        for text in texts:
            for word in set(text.split(' ')):
                if word not in self.knnUtilObj.word2idx:
                    self.knnUtilObj.word2idx[word] = len(self.knnUtilObj.word2idx)
                    self.knnUtilObj.doc_freq.append(0)
                self.knnUtilObj.doc_freq[self.knnUtilObj.word2idx[word]] += 1
        self.knnUtilObj.N=len(texts)
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

        for i in range(k):
            ans.append(scores[i][1])

        return ans

    def predict(self,X_test):
        answers=[]
        for _,row in X_test.iterrows():
            nearest_neighbours=self.GetNeighbours(row["StackFrames"],5)
            print(nearest_neighbours)
            answers.append(nearest_neighbours)
        return answers


if __name__ == '__main__':
    chunk = pd.read_csv("./temp_dataset.csv", chunksize=1000000,header=0)
    df = pd.concat(chunk)
    X_train, X_test = train_test_split(df, test_size=0.3, random_state=3) # 70% training and 30% test
    print(X_train.head())   
    KNNObj=KNN()
    KNNObj.fit(X_train)
    print("Fitting Done")
    answer_predicted=KNNObj.predict(X_test)
    print(answer_predicted)
