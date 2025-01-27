#This file executes the MOGA with NSGA-II for The Ramp (RP) under varying values of the parameters  
#L=loads, PI=tolerance threshold, MU= tolerance slope.
#SERVICES of Sock Shop are hard coded. For other systems just replace the list
#At each iteration, it calls the the R file 'detect_ramp.R' that executes the SPA detection for the algorithm with the selected paramters' values. 

import random
import pandas as pd
import argparse
import numpy as np
import pymoo
import matplotlib.pyplot as plt
import csv
from subprocess import PIPE, run
from numpy import savetxt
from pymoo.visualization.scatter import Scatter
from pymoo.core.problem import ElementwiseProblem
from pymoo.core.problem import Problem
from pymoo.core.mixed import MixedVariableGA
from pymoo.optimize import minimize
from pymoo.core.variable import Real, Integer, Choice, Binary
from pymoo.termination import get_termination
from pymoo.config import Config
from pymoo.util.plotting import plot
from pymoo.algorithms.moo.nsga2 import RankAndCrowdingSurvival

Config.warnings['not_compiled'] = False
#Loads
L = [50, 100, 150, 200, 250, 300]
# tolerated performance threshold
PI = [0.75, 1]
#regression estimated slope under fixed load
MU = [0.0000001, 0.00001]

SERVICES = ["createOrder", "basket", "getCatalogue", "getItem", "getCart", "login", "getOrders", "catalogue", "home", "tags", "getCustomer", "viewOrdersPage", "cataloguePage", "getRelated", "addToCart", "catalogueSize", "getAddress", "getCard", "showDetails"]

class RampProblem(ElementwiseProblem):

    def __init__(self, service = 'home'):
        # load, pi, mu
        vars = {
            "l": Choice(options=L),
            "pi": Real(bounds=(PI[0],PI[1])),
            "mu": Real(bounds=(MU[0],MU[1])),
        }
        super().__init__(vars=vars, n_obj=2, n_ieq_constr=2, xl = [50, 0.75, 0.0000001], xu = [300, 1, 0.00001])
        self.service = service
        self.scoresPP = []
        self.scoresRP = []

    def _evaluate(self, x, out, *args, **kwargs):
        command = "Rscript detect_ramp.R {} {} {} {}".format(self.service, x["l"], x["pi"], x["mu"])
        #print(command)
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        #print(result.stdout)
        scorePP = parse_result(result.stdout.split('\n'))[0]
        scoreRP = parse_result(result.stdout.split('\n'))[1]
        #print(parse_result(result.stdout))
        #Check the positive constraints of the fitness scores and return only is they are satisfied
        if scorePP > 0 and scoreRP > 0:
          self.scoresPP.append(scorePP)
          self.scoresRP.append(scoreRP)
          print("GA {} {} {} {} {} {}".format(self.service, x["l"], x["pi"], x["mu"], scorePP, scoreRP))
        out["F"] = [scorePP,scoreRP]
        out["G"] = [-scorePP,-scoreRP]
        
    
def parse_result(stdout):
  try:
    val1 = float(stdout[-4])
    val2 = float(stdout[-2])
  except:
    val1 = np.inf
    val2 = np.inf
  return [val1, val2]

def main():

    parser = argparse.ArgumentParser(description='Find ramp SPA parameters with metaheuristic optimizing search.')
    parser.add_argument("alg", help="selected search algorithm in [GA, RAND, GA+RAND]")
    parser.add_argument("-o", "--operation", type=str, help="analyzed operation ('all' to run for all operations)", required=True)
    parser.add_argument("-s", "--size", type=int, help="population size", required=False, default=20)
    parser.add_argument("-n", "--niterations", type=int, help="number of generations", required=False, default=20)
    parser.add_argument("-v", "--verbose", action='store_true', help="enables verbose log", required=False)
    parser.add_argument("-r", "--repeat", type=int, help="number of repeated runs", required=False, default=1)
    args = parser.parse_args()

    services = [args.operation]
   
    if args.operation == "all":
        services = SERVICES

    pattern='RP'
    if "GA" in args.alg:
      import os
      print(os.getcwd())
      csv_data_path = 'ParetoFront/populationGA_'+pattern+'.csv'
      with open(csv_data_path, 'w', newline='') as f:
        csv_writer = csv.writer(f,delimiter=';')
        csv_writer.writerow(['PP','RP','load','pi','mu'])
        csv_exe_path = 'ParetoFront/ExecutionTimesGA_'+pattern+'.csv'
        with open(csv_exe_path, 'w', newline='') as g:
          csv_writer1 = csv.writer(g,delimiter=';')
          csv_writer1.writerow([' ',"Execution time"])
          for s in services:
            plot= Scatter(title="Pareto Front - "+s)
            csv_writer.writerow([s,' ',' ',' ',' '])
            csv_writer1 = csv.writer(g,delimiter=';')
            csv_writer1.writerow([' ',"Execution time"])
            csv_writer1.writerow([s,' '])
            myZ=[]
            for r in range(args.repeat):
                print("*** GA run {} {} for RP ***".format(r,s))
                problem = RampProblem(s)
                algorithm = MixedVariableGA(pop_size=args.size, survival=RankAndCrowdingSurvival())
                #print(args.size)
                res = minimize(problem,
                           algorithm,
                           get_termination("n_gen", args.niterations),
                           seed = 1,
                           save_history=True,
                           verbose = args.verbose)
                exec_time="{:g}".format(res.exec_time)
                csv_writer1.writerow([' ',exec_time])
                print("GA {} total {} instances with RPscore {}".format(s, len(problem.scoresPP), problem.scoresRP))
                #Solutions in the Design spece
                print("Pareto hyperparameters: ",res.X)
                #Solutions in the objective space
                print("Pareto scores: \n", res.F)
                pop = res.pop
                print("all scores of final pop: \n", pop.get("F"))
                print("all hyperparameters of final pop: \n", pop.get("X"))
                if np.size(res.F)!=1 : 
                  #Pareto solutions
                  Y=np.ndarray.tolist(res.F)
                  Z=list()
                  for elm in res.X:
                    print(elm)
                    #print(np.where(res.X==elm))
                    i=np.where(res.X==elm)[0][0]
                    #print(i)
                    Z=Y[i]+list(elm.values())
                    myZ.append(Z)
                    #print(myZ)
                #plot.add(problem.pareto_front(), plot_type="line", color="black", alpha=0.7)
                plot.add(pop.get("F"), facecolor="none", edgecolor="blue")
                plot.add(res.F, facecolor="red", edgecolor="red")
                #print(myZ)
            plot.save('ParetoFront/ParetoFront_GA_RP_'+s+'.pdf')
            myZ=[row for row in myZ if not any(float('inf') == item for item in row)]
            csv_writer.writerows(myZ)
            #print(myZ)
        g.close()
      f.close()
          
    if "RAND" in args.alg:
         csv_data_path = 'ParetoFront/populationRAND_'+pattern+'.csv'
         with open(csv_data_path, 'w', newline='') as f:
           csv_writer = csv.writer(f,delimiter=';')
           csv_writer.writerow(['PP','RP','load','pi','mu'])
           for s in services:
             csv_writer.writerow([s,' ',' ',' ',' '])
             myZ=[]
             for r in range(args.repeat):
                print("*** RAND run {} for RP ***".format(r))
                scoresPP = []
                scoresRP = []
                d = {'col1': scoresPP, 'col2': scoresRP}
                results = pd.DataFrame(data=d)
                for i in range(args.size):
                    l = random.choice(L)
                    pi = random.uniform(PI[0], PI[1])
                    mu = random.uniform(MU[0], MU[1])
                    command = "Rscript detect_ramp.R {} {} {} {}".format(s, l, pi, mu)
                    #print(command)
                    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
                    scorePP = parse_result(result.stdout.split("\n"))[0]
                    scoreRP = parse_result(result.stdout.split("\n"))[1]
                    if scorePP > 0 and scoreRP > 0:
                      scoresPP.append(scorePP)
                      scoresRP.append(scoreRP)
                      print("RAND {} {} {} {} {} {}".format(s, scorePP, scoreRP, l, pi, mu))
                      temp="{:f} {:f} {:f} {:f} {:f} ".format(scorePP, scoreRP,l, pi, mu)
                      temp=temp.split()
                      temp=[float(item) for item in temp]
                      myZ.append(temp)
                print("RAND {} total {} of instances with RPscore {}".format(s, len(scoresRP), scoresRP))
             myZ=[row for row in myZ if not any(float('inf') == item for item in row)]
             #print(myZ)
             csv_writer.writerows(myZ)
    f.close()
                
if __name__ == "__main__":
    main()
