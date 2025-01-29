
# 
This repository contains the code to replicate the work 

_Multi-objective search to detect Software Performance anti-patterns (SPAs)_

# SPA detection
Execute NSGA-II to determine the optimal values of the parameters of the detection algorithms. It also provide the SPA instances. 

# Overview of the approach
![image](Approach.pdf)
# Requireemnts

# Project structure
```SPAdetection/

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

#Files

Python

_Maneger.py_ masters the execution of the Genetic Algoritm for each SPA considered. 
It calls the corresponding Python files: 
'GA_RP.py', 'GA_TJ.py', 'GA_AH.py', 'GA_CVR.py'. 
The 'path' field points to the folder in which these files are.

The files to run MOGA for each SPA:
_GA_RP.py_ Code to run the Genetic algorithm and determine the Pareto Front for the Ramp (RP) antipattern
_GA_CVR.py_ Code to run the Genetic algorithm and determine the Pareto Front for the Contiuous Violations Requirement (CVR) antipattern
_GA_TJ.py_ Code to run the Genetic algorithm and determine the Pareto Front for the Traffic Jam (TJ) antipattern
_GA_AH.py_ Code to run the Genetic algorithm and determine the Pareto Front for the Application Hiccups (AH) antipattern


The Python files repeatedly call the following R files that perform the actual SPA detection:

R

_Required libraries_
library(stringr)
library(gridExtra)
library(grid)
library(here)
library(Rmpfr)
library(xtable)
library(nls2)
library(readxl)
library(optparse)
library(ggplot2)
library(RColorBrewer)

_files_
detect_hiccup.R
detect_ramp.R
detect_tj.R
detect_cvr.R

The utitlity file contains the functions to execute the measurement framework
utilityFunctions.R


