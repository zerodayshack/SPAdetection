#This file executes the MOGA with NSGA-II for Traffic Jam (TJ) under varying values of the parameters 
#L=loads, PI=tolerance threshold, PHI= tolerance fraction, TAU= tolerance rate w= Bucket width.
#SERVICES of Sock Shop are hard coded. For other systems just replace the list
#At each iteration, it calls the the R file 'detect_tj.R' that executes the SPA detection for the algorithm with the selected paramters' values. 

import random
import argparse
import numpy as np
import pandas as pd
import csv
import pymoo
import csv
import openpyxl
from pymoo.visualization.scatter import Scatter
import matplotlib.pyplot as plt
from numpy import asarray
from numpy import savetxt
from subprocess import PIPE, run
from pymoo.visualization.scatter import Scatter
from pymoo.core.problem import ElementwiseProblem
from pymoo.core.mixed import MixedVariableGA
from pymoo.optimize import minimize
from pymoo.core.variable import Real, Integer, Choice, Binary
from pymoo.termination import get_termination
from pymoo.config import Config
from pymoo.util.plotting import plot
from pymoo.algorithms.moo.nsga2 import RankAndCrowdingSurvival

Config.warnings['not_compiled'] = False

# Traffic Jam assumes that a CVR instance has been detected. 
#Loads
L = [50,100,150,200,250,300]
# tolerance threshold
PI = [0.75, 1]
# tolerance fraction of buckets
PHI = [0.4, 0.6]
#tolerance rate over loads
TAU = [0,0.002]
# width of bucket over 361 points. We start from 2. LenghtExp=361 points eaach at 5 sec. Total time 1800 sec. min Bucket width (epsilon) 10 sec, max Bucket width 60 sec 
W = [2,3,4,5,6,7,8,9,10,11,12]

SERVICES = ["createOrder", "basket", "getCatalogue", "getItem", "getCart", "login", "getOrders", "catalogue", "home", "tags", "getCustomer", "viewOrdersPage", "cataloguePage", "getRelated", "addToCart", "catalogueSize", "getAddress", "getCard", "showDetails"]

class TJProblem(ElementwiseProblem):

    def __init__(self, service = 'Adjustment'):
        # load, pi, propTime, widthB, lengthExp
        vars = {
            "l": Choice(options=L),
            "pi": Real(bounds=(PI[0], PI[1])),
            "phi": Real(bounds=(PHI[0],PHI[1])),
            "tau": Real(bounds=(TAU[0],TAU[1])),
            "w": Choice(options=W)
        }
        super().__init__(vars=vars, n_var=5, n_obj=3, n_ieq_constr=3, xl = [50, 0.75, 0.4, 0, 1], xu = [300, 1, 0.6, 0.002, 12])
        self.service = service
        self.scoresPP = []
        self.scoresCVR = []
        self.scoresTJ = []

    def _evaluate(self, x, out, *args, **kwargs):
        command = "Rscript detect_tj.R {} {} {} {} {} {}".format(self.service, x["l"], x["pi"], x["phi"], x["tau"],x["w"])
        #print(command)
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        #print(result.stdout.split("\n"))
        scorePP = parse_result(result.stdout.split("\n"))[0]
        scoreCVR = parse_result(result.stdout.split("\n"))[1]
        scoreTJ = parse_result(result.stdout.split("\n"))[2]
        #print(scorePP, scoreCVR, scoreTJ)
        #if not pd.isna(scorePP) and  not pd.isna(scoreCVR) and scorePP > 0 and scoreCVR > 0:
        if scorePP > 0 and scoreCVR > 0 and scoreTJ > 0:
           self.scoresPP.append(scorePP)
           self.scoresCVR.append(scoreCVR)
           self.scoresTJ.append(scoreTJ)
        print("GA {} {} {} {} {} {} {} {} {} ".format(self.service, x["l"], x["pi"], x["phi"],x["tau"], x["w"], scorePP, scoreCVR, scoreTJ))
        out["F"] = [scorePP, scoreCVR, scoreTJ]
        out["G"] = [-scorePP, -scoreCVR, -scoreTJ]

def parse_result(stdout):
    try:
      val1 = float(stdout[-6])
      val2 = float(stdout[-4])
      val3 = float(stdout[-2])
    except:
      val1 = np.inf
      val2 = np.inf
      val3 = np.inf
    return [val1, val2, val3]

def main():
    parser = argparse.ArgumentParser(description='Find CRV SPA parameters with metaheuristic optimizing search.')
    parser.add_argument("alg", help="selected search algorithm in [GA, RAND, GA+RAND]")
    parser.add_argument("-o", "--operation", type=str, help="analyzed operation ('all' to run the search for all operation)", required=True)
    parser.add_argument("-s", "--size", type=int, help="population size", required=False, default=20)
    parser.add_argument("-n", "--niterations", type=int, help="number of iterations", required=False, default=20)
    parser.add_argument("-v", "--verbose", action='store_true', help="enables verbose log", required=False)
    parser.add_argument("-r", "--repeat", type=int, help="number of repeated runs", required=False, default=1)
    args = parser.parse_args()

    services = [args.operation]
    if args.operation == "all":
        services = SERVICES

    pattern='TJ'
    if "GA" in args.alg:
      csv_data_path = 'ParetoFront/populationGA_'+pattern+'.csv'
      with open(csv_data_path, 'w', newline='') as f:
        csv_writer = csv.writer(f,delimiter=';')
        csv_writer.writerow(['PP','CVR','TJ', 'load','pi','phi','tau','w'])
        csv_exe_path = 'ParetoFront/ExecutionTimesGA'+pattern+'.csv'
        with open(csv_exe_path, 'w', newline='') as g:
          csv_writer1 = csv.writer(g,delimiter=';')
          csv_writer1.writerow([' ',"Execution time"])
          for s in services:
            plot= Scatter(title="Pareto Front - "+s)
            csv_writer.writerow([s,' ',' ',' ',' ',' ',' ',' '])
            csv_writer1 = csv.writer(g,delimiter=';')
            csv_writer1.writerow([' ',"Execution time"])
            csv_writer1.writerow([s,' '])
            myZ=[]
            for r in range(args.repeat):
               print("*** GA run {} {} for TJ ***".format(r,s))
               problem = TJProblem(s)
               algorithm = MixedVariableGA(pop_size=args.size, survival=RankAndCrowdingSurvival())
               res = minimize(problem,
                     algorithm,
                     get_termination("n_gen", args.niterations),
                     seed = 1,
                     verbose = args.verbose,
                     save_history = True)
               print("GA {} total {} of instances with TJscore {}".format(s, len(problem.scoresTJ), problem.scoresTJ))
               #Solutions in the Design spece
               print("Pareto hyperparameters: ",res.X)
               #Solutions in the objective space
               print("Pareto scores: \n", res.F)
               pop = res.pop
               print("all scores of final pop: \n", pop.get("F"))
               print("all hyperparameters of final pop: \n", pop.get("X"))
               if np.size(res.F)!=1 : 
                 Y=np.ndarray.tolist(res.F)
                 Z=list()
                 for elm in res.X:
                    #print(elm)
                    #print(np.where(res.X==elm))
                    i=np.where(res.X==elm)[0][0]
                    #print(elm)
                    Z=Y[i]+list(elm.values())
                    myZ.append(Z)
               #plot.add(problem.pareto_front(), facecolor="none", edgecolor="green")
               #Plot population in objective space
               plot.add(pop.get("F"), facecolor="none", edgecolor="blue")
               #Plot pareto front in objective space
               plot.add(res.F, facecolor="red", edgecolor="blue")
            plot.save('ParetoFront/ParetoFront_GA_TJ'+s+'.pdf')
            myZ=[row for row in myZ if not any(float('inf') == item for item in row)]
            csv_writer.writerows(myZ)
        g.close()
      f.close()


    if "RAND" in args.alg:
      csv_data_path = 'ParetoFront/populationRAND_'+pattern+'.csv'
      with open(csv_data_path, 'w', newline='') as f:
         csv_writer = csv.writer(f,delimiter=';')
         csv_writer.writerow(['PP','CVR','TJ', 'load','pi','phi', 'tau', 'w'])
         for s in services:
           csv_writer.writerow([s,' ',' ',' ',' ',' ',' ',' '])
           myZ=[]
           for r in range(args.repeat):
             print("*** RAND run {} for TJ ***".format(r))
             scoresPP = []
             scoresCVR = []
             scoresTJ = []
             for i in range(args.size):
               l = random.choice(L)
               pi = random.uniform(PI[0], PI[1])
               tau = random.uniform(TAU[0], TAU[1])
               w = random.choice(W)
               phi = random.uniform(PHI[0], PHI[1])
               command = "Rscript detect_tj.R {} {} {} {} {} {}".format(s, l, pi, phi, tau, w)
               #print(command)
               result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
               scorePP = parse_result(result.stdout.split("\n"))[0]
               scoreCVR = parse_result(result.stdout.split("\n"))[1]
               scoreTJ = parse_result(result.stdout.split("\n"))[2]
               #print(scorePP, scoreCVR, scoreTJ)
               if scorePP > 0 and scoreCVR > 0 and scoreTJ > 0:
                 scoresPP.append(scorePP)
                 scoresCVR.append(scoreCVR)
                 scoresTJ.append(scoreTJ)
                 print("RAND {} {} {} {} {} {} {} {} {}".format(s, scorePP, scoreCVR, scoreTJ, l, pi, phi, tau, w))
                 temp="{:f} {:f} {:f} {:f} {:f} {:f} {:f} {:f} ".format(scorePP, scoreCVR, scoreTJ, l, pi, phi, tau, w)
                 temp=temp.split()
                 temp=[float(item) for item in temp]
                 #temp=[[] if not any(float('inf') == item for item in temp)]
                 myZ.append(temp)
             print("RAND {} total {} of instances with TJscore {}".format(s, len(scoresTJ), scoresTJ))
           myZ=[row for row in myZ if not any(float('inf') == item for item in row)]
           csv_writer.writerows(myZ)
      f.close()
    

if __name__ == "__main__":
    main()
