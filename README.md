
# 
This repository contains the code to replicate the work 

_Multi-objective search to detect Software Performance anti-patterns (SPAs)_
# Overview of the approach
![image](approach.pdf)
# Requireemnts

#Files
Maneger.py master the execution of the Genetic Algoritm for each SPA considered. It calls the corresponding Python files: 'GA_RP.py', 'GA_TJ.py', 'GA_AH.py', 'GA_CVR.py'. The 'path' filed points to folder in which the fiels are.

_GA_RP.py_ Code to run the Genetic algorithm and determine the Pareto Front for the Ramp (RP) antipattern
_GA_CVR.py_ Code to run the Genetic algorithm and determine the Pareto Front for the Contiuous Violations Requirement (CVR) antipattern
_GA_TJ.py_ Code to run the Genetic algorithm and determine the Pareto Front for the Traffic Jam (TJ) antipattern
_GA_AH.py_ Code to run the Genetic algorithm and determine the Pareto Front for the Application Hiccups (AH) antipattern

# SPA detection
Execute NSGA-II to determine the optimal values of the parameters of the detection algorithms. It also provide the SPA instances. 
