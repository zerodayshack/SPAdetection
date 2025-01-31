
# 
This repository contains the code to replicate the work 

_Multi-objective search to detect Software Performance anti-patterns (SPAs)_ B. Russo, M. Camilli, A. Janes. A. Avritzer

# SPA detection
Execute the multi-objective genetic algorithm NSGA-II to determine the optimal values of the parameters of detection algorithms. It also provide the SPA instances. Detection algorithms are defined per single Software Performance Antipattern (SPA). Compares the resulting algorithms with the ones determined with a random search. 

# Project structure
```
SPAdetection/
├── datasets/ 
│   └── dataset_300.csv 
│   └── dataset_250.csv 
│   └── dataset_200.csv
│   └── dataset_150.csv
│   └── dataset_100.csv
│   └── dataset_50.csv
│   └── dataset_2.csv
├── Manager.py
├── GA_RP.py
├── GA_TJ.py
├── GA_CVR.py
├── GA_AH.py
├── utilityFunctions.py
├── detect_ramp.R
├── detect_tj.R
├── detect_cvr.R
├── detect_hiccup.R
├── utilityfunctions.R
└── README.md
```

# Files

Python verison 3.8.15

_Maneger.py_ masters the execution of the Multi-Objective Genetic Algorithm (MOGA) for each SPA considered. 

_Required libraries_
os
pymoo Version: 0.6.0.1
pandas 1.5.3
csv
multiprocessing

It calls the Python files: 
'GA_RP.py', 'GA_TJ.py', 'GA_AH.py', 'GA_CVR.py'. 

The 'path' field needs points to the folder of the project.

The files to run MOGA for each SPA are:

_Required libraries_  
random  
pandas   
argparse  
numpy  
pymoo  
matplotlib.pyplot  
csv  
subprocess  

_GA_RP.py_ Code to run MOGA and RS and determine the Pareto Front and Dominance Set respectively for the Ramp (RP) antipattern  
_GA_CVR.py_ Code to run MOGA and RS and determine the Pareto Front and Dominance Set respectively  for the Contiuous Violations Requirement (CVR) antipattern  
_GA_TJ.py_ Code to run MOGA and RS and determine the Pareto Front and Dominance Set respectively for the Traffic Jam (TJ) antipattern  
_GA_AH.py_ Code to run MOGA and RS and determine the Pareto Front and Dominance Set respectively for the Application Hiccups (AH) antipattern  
The ranges that define the Design space are hard coded in each of he above files. 
The services of Sock Shop are hard coded in each of the above files  
The utility file _utilitFunctions.py_ contains all the fucnstions used in the above files  
Each of the above Python files  calls the corresponding R file below  

R version 4.3.1 (2023-06-16)
Platform: aarch64-apple-darwin20 (64-bit)

_Required libraries_  
library(stringr)  1.5.0
library(gridExtra)  2.3
library(grid)  4.3.1
library(here)  1.0.1
library(Rmpfr)   0.9.3
library(nls2)  0.3.3
library(readxl)  1.4.3
library(optparse)  1.7.3
library(ggplot2)  3.4.4
library(RColorBrewer)  1.1.3

_files_  
detect_hiccup.R  
detect_ramp.R  
detect_tj.R  
detect_cvr.R  

The utility file contains the functions to execute the measurement framework
_utilityFunctions.R_ and creates the datasets list used in the R files
Loads are hard coded in this file.  

# Overview of the approach  
![image](Approach.png)

# Data collection
The datasets in this project have been collected with PPTAM https://github.com/pptam/pptam-tool.  
The tool has collected the response times of the operations of Sock Shop demo https://github.com/ocp-power-demos/sock-shop-demo.  
The data contained in the .xan output files have been preprocessed and included in the datasets folder 
