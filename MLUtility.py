import re

"""
This file is created to save some common functions which are required for the ML Model

"""
def calculateLevenshteinDist(frames1, weights1, frames2, weights2):
    """ This function finds the Levenshtein Distance between two lists bases upon the given weights
    Parameters:
    frames1 (list) : List 1 for which Levenshtein Distance to be calculated
    weights1 (list) : List having weights for the list1
    frames2 (list) : List 2 for which Levenshtein Distance to be calculated
    weights2 (list) :  List having weights for the list2
    
    Returns:
    float: Levenshtein Distance between the frames1 and frames2
    
    """


    #initializing the 2D matrix 
    matrix = [[0.0 for _ in range(len(frames1) + 1)] for _ in range(len(frames2) + 1)]

    prev_column = matrix[0]

    for i in range(len(frames1)):
        prev_column[i + 1] = prev_column[i] + weights1[i]

    if len(frames1) == 0 or len(frames2) == 0:
        return sum(weights1)+sum(weights2)

    curr_column = matrix[1]
    # print("hey")
    # print(frames2)

    for i2 in range(len(frames2)):
        # print(i2," ",frames2[i2])   
        frame2 = frames2[i2]
        weight2 = weights2[i2]

        curr_column[0] = prev_column[0] + weight2

        for i1 in range(len(frames1)):

            frame1 = frames1[i1]
            weight1 = weights1[i1]

            if frame1 == frame2:
                curr_column[i1 + 1] = prev_column[i1]
            else:
                change = weight1 + weight2 + prev_column[i1]
                remove = weight2 + prev_column[i1 + 1]
                insert = weight1 + curr_column[i1]

                curr_column[i1 + 1] = min(change, remove, insert)

        if i2 != len(frames2) - 1:
            prev_column = curr_column
            curr_column = matrix[i2 + 2]

    return curr_column[-1]

def getErrorStr(errorCode):
    """ This function finds the string of special characters which are present in  the errorCode
    Parameters:
    errorCode (str) : The string from which we have to find the error
    
    Returns:
    str : the string of special characters which cant be present in varibale name
    
    """
    temp=""
    regrex="[a-zA-Z{}0-9;<>_\"\'\\n ]"
    l=len(errorCode)
    for c in range(l):
        z=re.match(regrex,errorCode[c])
        if not z:
            temp+=errorCode[c]
    res = ''.join(sorted(set(temp))) 
    s = set(temp) 
    return temp

def remove_equals(words):
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

def distDiff(str1, str2):
    """
    This function is a wrapper function for calculateLevenshteinDist which is created to
     find difference between two strings whose weights for complete string are equal
     Parametres:
     str1(str/list), str2(str/list): the strings/list whose difference to be calculated
     Returns:
     float: Levenshtein Distance between the str1 and str2
    
    """
    weights1=[1.0 for _ in range(len(str1))]
    weights2=[1.0 for _ in range(len(str2))]
    return calculateLevenshteinDist(str1,weights1,str2,weights2)
    