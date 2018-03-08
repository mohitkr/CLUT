import numpy as np
import itertools as it
from scipy import stats
import matplotlib.pyplot as plt

def indicator(X):
    ind=1
    if np.count_nonzero(X)==0:
        ind=0
    return ind

def minConsZero(X):
    mn=1000
    ind=0
    for i in range(len(X)):
        if np.count_nonzero(X[i])==0:
            ind+=1
        else:
            if ind>0:
                mn=min(ind,mn)
            ind=0
    if mn==1000:
        mn=0
    return mn

def maxConsZero(X):
    mx=0
    ind=0
    for i in range(len(X)):
        if np.count_nonzero(X[i])==0:
            ind+=1
            mx=max(ind,mx)
        else:
            ind=0
    return mx

def minConsNonZero(X):
    mn=1000
    ind=0
    for i in range(len(X)):
        if np.count_nonzero(X[i])!=0:
            ind+=1
        else:
            if ind>0:
                mn=min(ind,mn)
            ind=0
    if mn==1000:
        mn=0
    return mn

def maxConsNonZero(X):
    mx=0
    ind=0
    for i in range(len(X)):
        if np.count_nonzero(X[i])!=0:
            ind+=1
            mx=max(ind,mx)
        else:
            ind=0
    return mx    

def tensorIndicator(X,dim,var):
    outputMatSize=[]
    outputMatLoop = ()
    for i in range(len(dim)):
        outputMatSize.append(len(var[dim[i]]))
        outputMatLoop+=(range(len(var[dim[i]])),)
#     print "dim: ",dim
#     print "var: ",var
#     print "outputMatSize: ",outputMatSize
    outputTensor = np.zeros(outputMatSize)
    for multiIndex in it.product(*outputMatLoop):
        a=[]
        dimension = len(X.shape)
        for i in range(dimension):
            a.append(slice(0,X.shape[i]))
        for i in range(len(dim)):
            a[dim[i]]=multiIndex[i]
#         print "a: ",a
        if np.count_nonzero(X[tuple(a)])!=0:
            outputTensor[multiIndex]=1
            
    return outputTensor

def tensorSum(X,dim,var,ecInd):
    newdim = range(len(X.shape))
    newdim=list(set(newdim)-set(dim))
    dim=newdim
    outputMatSize=[]
    outputMatLoop = ()
    for i in range(len(dim)):
        outputMatSize.append(len(var[dim[i]]))
        outputMatLoop+=(range(len(var[dim[i]])),)
    outputTensor = np.zeros(outputMatSize)
    for multiIndex in it.product(*outputMatLoop):
        a=[]
        dimension = len(X.shape)
        for i in range(dimension):
            a.append(slice(0,X.shape[i]))
        for i in range(len(dim)):
            a[dim[i]]=multiIndex[i]
#         print "a: ",tuple(a)
        outputTensor[multiIndex]=np.sum(X[tuple(a)])
    if ecInd==1:
#         return stats.mode(outputTensor,axis=0)
        return outputTensor.max(axis=0)
#     print outputTensor.ravel()
    plt.hist(outputTensor.ravel(),bins='auto')
    plt.show()
#     fig = plt.gcf()
    return np.amax(outputTensor), np.amin(outputTensor)
#     return stats.mode(outputTensor,axis=None), np.amin(outputTensor)
  
def tensorConsZero(X,dim,var):
    newdim = range(len(X.shape))
    newdim=list(set(newdim)-set(dim))
    dim=newdim
    outputMatSize=[]
    outputMatLoop = ()
    for i in range(len(dim)):
        outputMatSize.append(len(var[dim[i]]))
        outputMatLoop+=(range(len(var[dim[i]])),)
    outputTensor1_min = np.zeros(outputMatSize)
    outputTensor2_min = np.zeros(outputMatSize)
    outputTensor1_max = np.zeros(outputMatSize)
    outputTensor2_max = np.zeros(outputMatSize)
    for multiIndex in it.product(*outputMatLoop):
        a=[]
        dimension = len(X.shape)
        for i in range(dimension):
            a.append(slice(0,X.shape[i]))
        for i in range(len(dim)):
            a[dim[i]]=multiIndex[i]
#         print "a: ",tuple(a)
        outputTensor1_min[multiIndex]=minConsZero(X[tuple(a)])
        outputTensor2_min[multiIndex]=minConsNonZero(X[tuple(a)])
        outputTensor1_max[multiIndex]=maxConsZero(X[tuple(a)])
        outputTensor2_max[multiIndex]=maxConsNonZero(X[tuple(a)])
            
    return np.amin(outputTensor1_min),np.amax(outputTensor1_max),np.amin(outputTensor2_min),np.amax(outputTensor2_max) 
    
def sumT(X,subset):
    return np.sum(X)

def maxT(X,subset):
    return np.sum(X)

def split(X,partSet,repeatDim):
    finalSet=()
    if len(partSet)==2:
        return finalSet
    if len(partSet)==1:
        for i in range(1,len(X)+1):
            lst=list(it.combinations(X, i))
            for j in range(len(lst)):
                finalSet=finalSet+((partSet+(lst[j],)),)
        return finalSet
    for i in range(1,len(X)):
        lst=list(it.combinations(X, i))
        for j in range(len(lst)):
#             print lst[j]
            s1=tuple(set(lst[j]+repeatDim))
            s2=[x for x in X if x not in s1]
            s1=(s1,)
            finalSet+=split(s2,s1,repeatDim)
    return finalSet


# def splitTensor(arr, cond):
#     return [arr[cond], arr[~cond]]
# 
# a = np.array([1,3,5,7,2,4,6,8])
# print splitTensor(a, a<5)
# 
# a = np.array([[1,2,3],[4,5,6],[7,8,9],[2,4,7]])
# print splitTensor(a, a[:,0]<3)




