#Functions needed to run the measurement framework and dominance analysis . 
#All sets are Pareto Fronts. 

import numpy as np
import math
from pymoo.indicators.gd import GD
from pymoo.indicators.gd_plus import GDPlus
import pandas as pd

#TEST sets
# paretoFront1=np.array([[0.2184,	115.465],[0.3105,	0.132], [0.2248,	0.2115],[0.2106,	524.924],[0.2201,	0.7863],[0.3419,	0.0075]])
# paretoFront2 = np.array([[0.171737,	738.834],[0.365067,	261.406]])

#EUCLIDEAN DISTANCE

#r2 indicator to compare two Pareto fronts through the sum of min distances of the first from the second front. Return a float value
def r2_indicator(pareto_front1, pareto_front2):
  try:
    if len(pareto_front1)!=0 and len(pareto_front2)!=0 :
      r2 = 0
      for item1 in pareto_front1:
        distances=[]
        min_distance = 0
        for item2 in pareto_front2 :
          #print(item1)
          #print(pareto_front2)
          distances.append(euclidean_distance(item1,item2))
        minDistance = min(distances)
        #print(minDistance)
        r2 +=  minDistance
      #print(r2)
      return r2
    else :
      return float('inf')
  except:
    print("Exception: array empty R2")

#Normalization of the indicator. Normalization is useful to comapre this measures with the others    
def r2_indicatorNorm(pareto_front1, pareto_front2):
  if len(paretoFront1)!=0 and len(paretoFront2)!=0:
    unionFronts=np.concatenate((paretoFront1,paretoFront2), axis=0)
    #normalize for min,max of the union of the pareto fronts
    normParetoFrontUnion=normalize(unionFronts)
    normParetoFront1=np.array_split(np.asarray(normParetoFrontUnion).T,[len(paretoFront1)],axis=1)[0][0]
    normParetoFront2=np.array_split(np.asarray(normParetoFrontUnion).T,[len(paretoFront1)],axis=1)[1][0]
    return r2_indicator(normParetoFront1,normParetoFront2)
  else :
    return float('inf')

#GENERALIZATION DISTANCE
#Compute the Generational Distance (the average distance from any point in Pareto RAND (pareto_front2) to the closest point in the Pareto GA (pareto_front1).)
#Return a float value. see https://pymoo.org/misc/indicators.html
def gdPareto(pareto_front1, pareto_front2):
  try:
    if np.size(pareto_front1)!=0 and np.size(pareto_front2)!=0 :
      #ind = GD(pareto_front1) this is not pareto compliant see paper "How to Evaluate Solutions in Pareto-based Search-Based Software Engineering? A Critical Review and Methodological Guidance"
      ind=GDPlus(pareto_front1)
      return ind(pareto_front2)
    else:
      return float('inf')
  except: 
    print(np.size(pareto_front1), np.size(pareto_front2), pareto_front2,"array empty for gd")
    #return float('inf')
#Normalization of the indicator. Normalization is useful to comapre this measures with the others    
def gdParetoNorm(pareto_front1, pareto_front2):
  if len(paretoFront1)!=0 and len(paretoFront2)!=0:
    unionFronts=np.concatenate((paretoFront1,paretoFront2), axis=0)
    #normalize for min,max of the union of the pareto fronts
    normParetoFrontUnion=normalize(unionFronts)
    normParetoFront1=np.array_split(np.asarray(normParetoFrontUnion).T,[len(paretoFront1)],axis=1)[0][0]
    normParetoFront2=np.array_split(np.asarray(normParetoFrontUnion).T,[len(paretoFront1)],axis=1)[1][0]
    return gdPareto(normParetoFront1,normParetoFront2)
  else:
    return float('inf')

##DISTANCE FROM IDEAL POINT
#Distance from the ideal point. Returns a float value
def minDistanceFromIdeal(paretoFront, point): 
  try:
    if np.size(paretoFront)!=0:
      distances=[]
      minDistance = float('inf')
      if not len(paretoFront)==0 :
        distances=[]
        for item1 in paretoFront:
          min_distance = 0
          distances.append(euclidean_distance(item1,point))
        minDistance = min(distances)
      return minDistance
    else:
      return float('inf')
  except:
    return float('inf')
    print("array empty for min dist")

#EPSILON
#epsilon - indicator, e(paretoFront1,paretoFront2)<=0 paretoFront1 weakly dominates paretoFront2
def eIndicator(paretoFront1,paretoFront2) :
  try:
    if len(paretoFront1)!=0 and len(paretoFront2)!=0:
      colMax=[]
      #print(len(paretoFront1[0])-1)
      for i in range(0,len(paretoFront1[0])):
        col1 = paretoFront1[:,i] 
        col2 = paretoFront2[:,i]
        #print(col1)
        #print(col2)
        temp=[]
        for item2 in col2:
          temp.append(np.min(col1-item2))
        #print(temp)
        colMax.append(max(temp))
      #print(colMax)
      eIndicator = max(colMax)
      return eIndicator
    else:
      return float('inf')
  except:
    return float('inf')
    print("array empty")
#Normalization of the indicator. Normalization is useful to comapre this measures with the others    
def eIndicatorNorm(paretoFront1,paretoFront2) :
  normParetoFront1=normalizeTwoArrays(paretoFront1, paretoFront2)[0]
  normParetoFront2=normalizeTwoArrays(paretoFront1, paretoFront2)[1]
  return eIndicator(normParetoFront1,normParetoFront2)

#SUPPORTING FUNCTIONS

#Point must be two 2-uples (2d) of the same length (better length 1). Return an array of the euclidean distances calculate row by row
def euclidean_distance(point1, point2):
  return np.sqrt((point1[0]-point2[0])**2+(point1[1]-point2[1])**2)

####Normalization of the objectives for non cardinal indicators see https://dl.acm.org/doi/pdf/10.1145/3300148 with max-min
#supporting normalization
def normalize(paretoFront):
  paretoFrontByCol=[]
  normParetoFront=[]
  if len(paretoFront)!=0 :
      paretoFrontByCol=np.split(paretoFront, paretoFront.shape[1], axis=1)
      normParetoFront = [(array-min(array))/(max(array)-min(array)) if len(array) != 1 else array for array in paretoFrontByCol ]
  else :
    normParetoFront=paretoFront
  return normParetoFront 

#This is used for two arrays
def normalizeTwoArrays(paretoFront1, paretoFront2):
  if len(paretoFront1)!=0 and len(paretoFront2)!=0:
    unionFronts=np.concatenate((paretoFront1,paretoFront2), axis=0)
    #normalize for min,max of the union of the pareto fronts
    normParetoFrontUnion=normalize(unionFronts)
    normParetoFront1=np.array_split(np.asarray(normParetoFrontUnion).T,[len(paretoFront1)],axis=1)[0][0]
    normParetoFront2=np.array_split(np.asarray(normParetoFrontUnion).T,[len(paretoFront1)],axis=1)[1][0]
  else:
    if len(paretoFront1)==0 and len(paretoFront2)==0:
      return float('inf'), float('inf')
    else: 
      if len(paretoFront1)==0:
        return float('inf'), paretoFront2
      else: 
        return paretoFront1, float('inf')
  return normParetoFront1, normParetoFront2

#Creation of Pareto Front for RAND
#vector 1 and 2 must be np.array
def is_dominated(vector1, vector2):
    return all(bi <= ai for ai, bi in zip(np.array(vector1), np.array(vector2))) and any(bi < ai for ai, bi in zip(np.array(vector1), np.array(vector2)))
    #return all(np.array(vector2) <= np.array(vector1))
def isnot_dominated(vector, vector_set):
  #temp=all(is_dominated(v,vector) for v in vector_set if not np.array_equal(v, vector))
  #print(temp)
  temp=any(is_dominated(v,vector) for v in vector_set if not np.array_equal(v, vector))
  if not temp:
    return True, vector
  else: 
    return False, None
#vector is not dominating vector_set
def dominates(vector, vector_set):
  temp=all(is_dominated(v,vector) for v in vector_set if not np.array_equal(v, vector))
  #print(temp)
  #temp1=any(is_dominated(v,vector) for v in vector_set if not np.array_equal(v, vector))
  if temp:
    return True , vector
  else: 
    return False, None


