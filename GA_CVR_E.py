#This file executes the MOGA with NSGA-II for Continuous Violated Requirement (CVR) under varying values of the parameters 
#L=loads, PI=tolerance threshold, PHI= tolerance fraction, w= Bucket width.
#SERVICES of Ericsson Telecommunication System are hard coded. For other systems just replace the list
#At each iteration, it calls the the R file 'detect_cvr.R' that executes the SPA detection for the algorithm with the selected paramters' values. 

import random
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import csv
from subprocess import PIPE, run
from numpy import savetxt
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

#Loads
L = [50,60,70,80,90,100]
# tolerated performance threshold
PI = [0.75, 1]
# proportion of tolerated violating buckets
PHI = [0.4, 0.6]
# Max time = 1255. Bucket scale = 50. Max bucket length = 9*50.
W = [4,5,6,7,8,9,10,11,12]

SERVICES = ["Adjustment","Enquiry","DBDataManagement","Interrogation",
"Control","InternalCommunication","StatusUpdates","Offline","Online",
"Recompose","ResourcesRead","ResourcesUpdate"]

class CVRProblem(ElementwiseProblem):

    def __init__(self, service = 'Enquiry'):
        # pi, propTime, widthB, lengthExp
        vars = {
           # "l": Choice(options=L),
            "pi": Real(bounds=(PI[0], PI[1])),
            "phi": Real(bounds=(PHI[0],PHI[1])),
            "w": Choice(options=W)
        }
        super().__init__(vars=vars, n_var=3, n_obj=2, n_ieq_constr=2, xl = [0.75, 0.5, 4], xu = [ 1, 0.90, 12])
        self.service = service
        self.scoresPP = []
        self.scoresCVR = []

    def _evaluate(self, x, out, *args, **kwargs):
        command = "Rscript detect_cvr_E.R {} {} {} {}".format(self.service,  x["pi"], x["phi"], x["w"])
        #print(command)
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        #print(result.stdout.split("\n"))
        scorePP = parse_result(result.stdout.split("\n"))[0]
        scoreCVR = parse_result(result.stdout.split("\n"))[1]
        #print(scorePP, scoreCVR)
        #if not pd.isna(scorePP) and  not pd.isna(scoreCVR) and scorePP > 0 and scoreCVR > 0:
        if scorePP > 0 and scoreCVR > 0:
           self.scoresPP.append(scorePP)
           self.scoresCVR.append(scoreCVR)
           print("GA {} {} {} {} {} {}".format(self.service,  x["pi"], x["phi"], x["w"], scorePP, scoreCVR))
        out["F"] = [scorePP,scoreCVR]
        out["G"] = [-scorePP,-scoreCVR]

def parse_result(stdout):
    try:
      val1 = float(stdout[-4])
      val2 = float(stdout[-2])
    except:
      val1 = np.inf
      val2 = np.inf
    return [val1, val2]


def main():
    parser = argparse.ArgumentParser(description='Find CRV SPA parameters with metaheuristic optimizing search.')
    parser.add_argument("alg", help="selected search algorithm in [GA, RAND, GA+RAND]")
    parser.add_argument("-o", "--operation", type=str, help="analyzed operation ('all' to run the search for all operation)", required=True)
    #arg.size is the population of genomes both for GA and RAND
    parser.add_argument("-s", "--size", type=int, help="population size", required=False, default=20)
    #args.niterations is the stopping criterio for the evaluation of one population of genomes  in GA
    parser.add_argument("-n", "--niterations", type=int, help="number of iterations for the minimization process", required=False, default=20)
    #args.repeat repeate the whole evaluation of a population both in GA and RAND. we use default
    parser.add_argument("-r", "--repeat", type=int, help="number of repeated runs", required=False, default=1)
    parser.add_argument("-v", "--verbose", action='store_true', help="enables verbose log", required=False)
    args = parser.parse_args()

    services = [args.operation]
    if args.operation == "all":
        services = SERVICES
   
    pattern='CVR'
    if "GA" in args.alg:
      csv_data_path = 'ParetoFront/Ericsson/populationGA_E'+pattern+'.csv'
      with open(csv_data_path, 'w', newline='') as f:
        csv_writer = csv.writer(f,delimiter=';')
        csv_writer.writerow(['PP','CVR','pi','phi','w'])
        csv_exe_path = 'ParetoFront/Ericsson/ExecutionTimesGA_E'+pattern+'.csv'
        with open(csv_exe_path, 'w', newline='') as g:
          csv_writer1 = csv.writer(g,delimiter=';')
          csv_writer1.writerow([' ',"Execution time"])
          for s in services:
            plot= Scatter(title="Pareto Front -"+s)
            csv_writer.writerow([s,' ',' ',' ',' '])
            csv_writer1.writerow([s,' '])
            myZ=[]
            for r in range(args.repeat):
                 print("*** GA run {} {} for CVR ***".format(r,s))
                 problem = CVRProblem(s)
                 algorithm = MixedVariableGA(pop_size=args.size, survival=RankAndCrowdingSurvival())
                 res = minimize(problem,
                     algorithm,
                     get_termination("n_gen", args.niterations),
                     seed = 1,
                     save_history=True,
                     verbose = args.verbose)
                 exec_time="{:g}".format(res.exec_time)
                 csv_writer1.writerow([' ',exec_time])
                 print("GA {} total {} of instances with CVRscore {}".format(s, len(problem.scoresCVR), problem.scoresCVR))
                 #Solutions in the Design spece
                 print("Pareto hyperparameters: \n",res.X)
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
                     #print(i)
                     Z=Y[i]+list(elm.values())
                     myZ.append(Z)
                     #print(myZ)
                 plot.add(pop.get("F"), facecolor="none", edgecolor="blue")
                 plot.add(res.F, facecolor="red", edgecolor="red")
                 #plot.show()
                 #print(myZ)
            plot.save('ParetoFront/Ericsson/ParetoFront_GA_CVR_E'+s+'.pdf')
            myZ=[row for row in myZ if not any(float('inf') == item for item in row)]
            csv_writer.writerows(myZ)
        g.close()
      f.close()

    if "RAND" in args.alg:
      csv_data_path = 'ParetoFront/Ericsson/populationRAND_E'+pattern+'.csv'
      with open(csv_data_path, 'w', newline='') as f:
          csv_writer = csv.writer(f,delimiter=';')
          csv_writer.writerow(['PP','CVR','pi','phi','w'])
          for s in services:
            csv_writer.writerow([s,' ',' ',' '])
            myZ=[]
            lenscoresCVR=0
            for r in range(args.repeat):
                print("*** RAND run {} for CVR ***".format(r))
                scoresPP = []
                scoresCVR = []
                for i in range(args.size):
                   # l = random.choice(L)
                    pi = random.uniform(PI[0], PI[1])
                    phi = random.uniform(PHI[0], PHI[1])
                    w = random.choice(W)
                    command = "Rscript detect_cvr_E.R {} {} {} {}".format(s, pi, phi, w)
                    #print(command)
                    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
                    scorePP = parse_result(result.stdout.split("\n"))[0]
                    scoreCVR = parse_result(result.stdout.split("\n"))[1]
                    #print(scorePP, scoreCVR)
                    #if not pd.isna(scorePP) and  not pd.isna(scoreCVR) and scorePP > 0 and scoreCVR > 0:
                    if scorePP > 0 and scoreCVR > 0:
                       scoresPP.append(scorePP)
                       scoresCVR.append(scoreCVR)
                       print("RAND {} {} {} {} {} {}".format(s, pi, phi, w, scorePP, scoreCVR))
                       temp="{:f} {:f} {:f} {:f} {:f} ".format(scorePP, scoreCVR, pi, phi, w)
                       temp=temp.split()
                       temp=[float(item) for item in temp]
                       myZ.append(temp)       
                print("RAND {} total {} of instances with CVRscore {}".format(s, len(scoresCVR), scoresCVR))
                #print('Threads:', result.exec_time)
            myZ=[row for row in myZ if not any(float('inf') == item for item in row)]
            #print(myZ)
            csv_writer.writerows(myZ)   
      f.close()

if __name__ == "__main__":
    main()
