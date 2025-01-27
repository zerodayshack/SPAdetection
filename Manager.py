import os
import pymoo
import pandas as pd
import csv
from multiprocessing import Process

path = "/Users/babsi/Research/Dropbox/Papers/Matteo/spa_search_detection-main/detection/"
#tasks = ['GA_RP.py', 'GA_TJ.py', 'GA_AH.py', 'GA_CVR.py']
tasks = ['GA_RP_E.py', 'GA_CVR_E.py', 'GA_TJ_E.py', 'GA_AH_E.py']
options = [' -o all -s 50 -n 20 GA', ' -o all -s 50  RAND']

#OPTIONS description
 #alg", help="selected search algorithm in [GA, RAND, GA+RAND]"
#"-o", "--operation", type=str, help="analyzed operation ('all' to run for all operations)", required=True
#"-s", "--size", type=int, help="population size", required=False, default=20
#"-n", "--niterations", type=int, help="number of iterations", required=False, default=20; iterations=number of time the GA minimizes 
#"-v", "--verbose", action='store_true', help="enables verbose log", required=False
#"-r", "--repeat", type=int, help="number of repeated runs", required=False, default=1; repeat= number of times the evolution is repeated
  

def foo(task,option):
    os.system('python ' + path + task + option)
    #os.system('python ' + path + 'GA_TJ.py -o getAddress -s 10  -n 1  GA')

if __name__ == '__main__':    
  for task in tasks:
    for option in options:
      p = Process(target=foo, args=(task,option))
      p.start()
      p.join()

