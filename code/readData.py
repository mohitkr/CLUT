import sys
import csv
import numpy as np
from collections import OrderedDict
import constraintFormulation as cf
import operator
from numpy.core.defchararray import index
import time
# import xlsxwriter

def readCSV(fileName):
    with open(fileName, 'rU') as csvFile:
        reader = csv.reader(csvFile, delimiter=',')
        data = list(reader)
        data = np.asarray(data)
        return data
        
def cleanData(data):
    variables=[]
    rows, cols = data.shape
#     finding number of variables
    blankRows=0
    while(not data[blankRows,0]):
        blankRows+=1
    blankCols=0
    while(not data[0,blankCols]):
        blankCols+=1
    for i in range(blankRows):
        variables.append(list(OrderedDict.fromkeys(data[i,blankCols:])))
    for i in range(blankCols):
        variables.append(list(OrderedDict.fromkeys(data[blankRows:,i])))
    variables_mat=np.matrix(variables)

    lengths = []
    for i in range(variables_mat.shape[1]):
        lengths.append(len(variables_mat[0,i]))
    dataTensor=np.zeros(lengths)
    
    for i in range(blankRows, rows):
        for j in range(blankCols, cols):
            if data[i,j].astype(int)==1:
                index=()
                for k in range(blankRows):
                    index=index+(variables[k].index(data[k,j]),)
                for k in range(blankCols):
                    index=index+(variables[blankRows+k].index(data[i,k]),)
                dataTensor[index]=1
    return dataTensor,variables

def findConstraints(dataTensor,variables,orderingNotImp,extraConstraints,repeatDim):
    r=set([v for v in range(len(variables)) if v not in repeatDim])
    subsets=cf.split(r,(),repeatDim)
    for l in range(len(subsets)):
        subset=subsets[l]
        newset=subset[0]+subset[1]
        # this value will be used to filter max constraints
        maxPossible=1
        for i in range(len(subset[1])):
            maxPossible*=len(variables[subset[1][i]])   
        idTensor=cf.tensorIndicator(dataTensor,newset, variables)
        sumSet = range(len(subset[0]),len(newset))
        if subset[0] in extraConstraints:
            sumTensor=cf.tensorSum(idTensor,sumSet, np.array(variables)[list(newset)],1)
            print('M:',subset[0],' S:',subset[1])
            print(sumTensor)
        else:
            sumTensor_max,sumTensor_min=cf.tensorSum(idTensor,sumSet, np.array(variables)[list(newset)],0)
            if (sumTensor_min != 0 and sumTensor_min!=maxPossible) or (sumTensor_max != maxPossible and sumTensor_max!=0): 
                print('M:',subset[0],' S:',subset[1])
            if sumTensor_min != 0 and sumTensor_min!=maxPossible: 
                print('min: ',sumTensor_min)
            if sumTensor_max != maxPossible and sumTensor_max!=0: 
                print('max: ',sumTensor_max)      
        
        if len(set(subset[1]))==1 and len(set(orderingNotImp) & set(subset[1]))==0:
            minConsZero,maxConsZero,minConsNonZero,maxConsNonZero = cf.tensorConsZero(idTensor,sumSet, np.array(variables)[list(newset)])
            if (minConsZero!=0 and minConsZero!=maxPossible) or (maxConsZero!=maxPossible and maxConsZero>0) or (minConsNonZero!=0 and minConsNonZero!=maxPossible) or (maxConsNonZero!=maxPossible and maxConsNonZero>0):
                print('M:',subset[0],' S:',subset[1])
            if minConsZero!=0 and minConsZero!=maxPossible:
                print('min cons Zero: ',minConsZero)
            if maxConsZero!=maxPossible and maxConsZero>0:
                print('max cons Zero: ',maxConsZero)
            if minConsNonZero!=0 and minConsNonZero!=maxPossible:
                print('min cons NonZero: ',minConsNonZero)
            if maxConsNonZero!=maxPossible and maxConsNonZero>0:
                print('max cons NonZero: ',maxConsNonZero)

def createList(data):
    output=[]
    values=[]
    vals=[]
    n=data.shape[0]
    for i in range(n):
        if i==0:
            values.append(data[i,0])
            vals.append(data[i,1])
        elif i!=0 and data[i,1]==data[i-1,1] and i!=n-1:
            values.append(data[i,0])
        elif i!=0 and data[i,1]==data[i-1,1] and i==n-1:
            values.append(data[i,0])
            output.append(values)
        else:
            output.append(values)
            values=[]
            values.append(data[i,0])
            vals.append(data[i,1])
    return output, vals
 
def vectorizeExtraInfo(extraInfo,variables):
    dim=int(extraInfo[0,0])
    extraInfo=extraInfo[1:,:]
    sortedData=np.array(sorted(extraInfo, key=operator.itemgetter(1)))
    lst,vals=createList(sortedData)
    variable=variables[dim]
    filterTensors=[]
    for k in range(len(lst)):
        filterTensor = np.zeros((len(lst[k]),len(variable)))
        i=0
        j=0
        while i<len(lst[k]) or j<len(variable):
            if variable[j] in lst[k]:
                filterTensor[i,j]=1
                i+=1
            j+=1
        filterTensors.append(filterTensor)
    return filterTensors,lst,vals

def main():
    start=time.clock()
    fileName=sys.argv[1]
    numTables=int(sys.argv[2])
    data = readCSV(fileName)
    dataTensor,variables=cleanData(data)
    lenVar=[]
    for i in range(len(variables)):
        lenVar.append(len(variables[i]))
    print("Size of the variables: ",lenVar)

    extraConstraints = [(0,1)]
    orderingNotImp=[2]
    repeatDim=()
    print("\nNo filter: " )   
    findConstraints(dataTensor,variables,orderingNotImp,extraConstraints,repeatDim)
    
    for i in range(numTables-1):
        fileName = sys.argv[i+3]
        extraInfo = readCSV(fileName)
        filterTensors,lst,vals=vectorizeExtraInfo(extraInfo,variables)
        for i in range(len(vals)):
            dim=int(extraInfo[0,0])
            updatedVariables=variables[:]
            updatedVariables[dim]=[x for x in variables[dim] if x in lst[i]]
            mat=np.tensordot(filterTensors[i],dataTensor, [1,dim])
            for j in range(dim):
                mat=np.swapaxes(mat,j,j+1)
            print(mat.shape)
            print("\nConstraints for filter: ", vals[i])
            findConstraints(mat,updatedVariables,orderingNotImp,extraConstraints,repeatDim)
    print("\nTime Taken: ",time.clock()-start,' secs')
if __name__==main():
    main()















