#This file executes the MOGA with NSGA-II for Application Hiccups (AH) under varying values of the parameters 
#L=loads, PI=tolerance threshold, CHI= tolerance duration, w= Bucket width.
#SERVICES of Ericsson Telecommunication System are hard coded. For other systems just replace the list
#At each iteration, it calls the the R file 'detect_hiccup.R' that executes the SPA detection for the algorithm with the selected paramters' values. 

import random
import argparse
import numpy as np
import pandas as pd
import csv
import pymoo
import csv
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

#Loads
L = [40,50,60,70,80,90,100]
# tolerated performance threshold
PI = [0.75, 1]
# proportion of time limiting the total duration of hiccups
CHI = [0.75,0.90]
# Max time = 1255. Bucket scale = 50. Max bucket length = 9*50.
W = [4,5,6,7,8,9,10,11,12]

SERVICES = ["Adjustment","Enquiry","DBDataManagement","Interrogation",
"Control","InternalCommunication","StatusUpdates","Offline","Online",
"Recompose","ResourcesRead","ResourcesUpdate"]

class AHProblem(ElementwiseProblem):

    def __init__(self, service = 'Enquiry'):
        # load, pi, propTime, widthB
        vars = {
            #"l": Choice(options=L),
            "pi": Real(bounds=(PI[0], PI[1])),
            "chi": Real(bounds=(CHI[0],CHI[1])),
            "w": Choice(options=W),
        }
        super().__init__(vars=vars, n_var=3, n_obj=2, n_ieq_constr=2, xl = [0.75, 0.75, 4], xu = [1, 0.90, 12])
        self.service = service
        self.scoresPP = []
        self.scoresAH = []
       

    def _evaluate(self, x, out, *args, **kwargs):
        command = "Rscript detect_hiccup_E.R {} {} {} {}".format(self.service, x["pi"], x["chi"], x["w"])
        #print(command)
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        #print(result.stdout.split(" "))
        scorePP = parse_result(result.stdout.split("\n"))[0]
        scoreAH = parse_result(result.stdout.split("\n"))[1]
        #print(scorePP, scoreAH)
        #if not pd.isna(scorePP) and  not pd.isna(scoreCVR) and scorePP > 0 and scoreCVR > 0:
        if scorePP > 0 and scoreAH > 0:
           self.scoresPP.append(scorePP)
           self.scoresAH.append(scoreAH)
        print("GA {} {} {} {} ".format(self.service, x["pi"], x["chi"], x["w"]))
        out["F"] = [scorePP, scoreAH]
        out["G"] = [-scorePP, -scoreAH]

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
    parser.add_argument("-s", "--size", type=int, help="population size", required=False, default=20)
    parser.add_argument("-n", "--niterations", type=int, help="number of iterations", required=False, default=20)
    parser.add_argument("-v", "--verbose", action='store_true', help="enables verbose log", required=False)
    parser.add_argument("-r", "--repeat", type=int, help="number of repeated runs", required=False, default=1)
    args = parser.parse_args()

    services = [args.operation]
    if args.operation == "all":
        services = SERVICES

    pattern='AH'
    if "GA" in args.alg:
      csv_data_path = 'ParetoFront/Ericsson/populationGA_E'+pattern+'.csv'
      with open(csv_data_path, 'w', newline='') as f:
        csv_writer = csv.writer(f,delimiter=';')
        csv_writer.writerow(['PP','AH','pi','chi', 'w'])
        csv_exe_path = 'ParetoFront/Ericsson/ExecutionTimesGA_E'+pattern+'.csv'
        with open(csv_exe_path, 'w', newline='') as g:
          csv_writer1 = csv.writer(g,delimiter=';')
          csv_writer1.writerow([' ',"Execution time"])
          for s in services:
            plot= Scatter(title="Pareto Front - "+s)
            csv_writer.writerow([s,' ',' ',' '])
            csv_writer1 = csv.writer(g,delimiter=';')
            csv_writer1.writerow([' ',"Execution time"])
            csv_writer1.writerow([s,' '])
            myZ=[]
            for r in range(args.repeat):
               print("*** GA run {} {} for AH ***".format(r,s))
               problem = AHProblem(s)
               algorithm = MixedVariableGA(pop_size=args.size, survival=RankAndCrowdingSurvival())
               res = minimize(problem,
                     algorithm,
                     get_termination("n_gen", args.niterations),
                     seed = 1,
                     save_history=True,
                     verbose = args.verbose)
               print("GA {} total {} of instances with AHscore {}".format(s, len(problem.scoresAH), problem.scoresAH))
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
                   #print(elm)
               #plot.add(problem.pareto_front(), plot_type="line", color="black", alpha=0.7)
               plot.add(pop.get("F"), facecolor="none", edgecolor="blue")
               plot.add(res.F, facecolor="red", edgecolor="blue")
            plot.save('ParetoFront/Ericsson/ParetoFront_GA_AH_E'+s+'.pdf')
            myZ=[row for row in myZ if not any(float('inf') == item for item in row)]
            csv_writer.writerows(myZ)
            #print(myZ)
        g.close()
      f.close()
          
    if "RAND" in args.alg:
      csv_data_path = 'ParetoFront/Ericsson/populationRAND_E'+pattern+'.csv'
      with open(csv_data_path, 'w', newline='') as f:
        csv_writer = csv.writer(f,delimiter=';')
        csv_writer.writerow(['PP','AH','pi','chi', 'w'])
        for s in services:
            csv_writer.writerow([s,' ',' ',' ',' ',' '])
            myZ=[]
            for r in range(args.repeat):
              print("*** RAND run {} for AH ***".format(r))
              scoresPP = []
              scoresAH = []
              for i in range(args.size):
                 # l = random.choice(L)
                  pi = random.uniform(PI[0], PI[1])
                  chi = random.uniform(CHI[0], CHI[1])
                  w = random.choice(W)
                  command = "Rscript detect_hiccup_E.R {} {} {} {}".format(s, pi, chi, w)
                  #print(command)
                  result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
                  #print(result.stdout.split("\n"))
                  scorePP = parse_result(result.stdout.split("\n"))[0]
                  scoreAH = parse_result(result.stdout.split("\n"))[1]
                  if scorePP > 0 and scoreAH > 0:
                    scoresPP.append(scorePP)
                    scoresAH.append(scoreAH)
                    print("RAND {} {} {} {} {} {}".format(s, scorePP, scoreAH, pi, chi, w))
                    temp="{:f} {:f} {:f} {:f} {:f}".format(scorePP, scoreAH, pi, chi, w)
                    temp=temp.split()
                    temp=[float(item) for item in temp]
                    myZ.append(temp)
              print("RAND {} total {} of instances with AHscore {}".format(s, len(scoresAH), scoresAH))
            myZ=[row for row in myZ if not any(float('inf') == item for item in row)]
            csv_writer.writerows(myZ)  
      f.close()

if __name__ == "__main__":
    main()
