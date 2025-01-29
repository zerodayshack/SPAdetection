#This file executes the detection for Traffic Jam (TJ) and individual service or operation of a system. 
#It is called by the GA_TJ Python files.  

# Definitions 
# serviceName: operation or microservice; string
# Load: load: integer
# pi: 1 - tolerance threshold; real
# prop: tolerance fraction of buckets, real
# r: tau tolerance rate, real
# widthB: epsilon, size of a bucket; integer

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

# args
args = commandArgs(trailingOnly=TRUE)
if (length(args) != 6) {
  stop("Usage: Rscript detect_tj.R <serviceName> <load> <pi> <prop> <r> <widthB>", call.=FALSE)
} else {
  serviceName <- args[1]
  load <- as.numeric(args[2])
  pi <- as.numeric(args[3])
  prop <- as.numeric(args[4])
  widthB <- as.numeric(args[6])
  r <- as.numeric(args[5])
}

#TEST INPUT
# load=300
# pi=0.9
# prop=0.6
# r=0.0004
# widthB=5

#Set your directory
setwd("~/")
#Set code directory
directory <- file.path(paste(getwd(), "../SPAdetection",sep=""), fsep = .Platform$file.sep)

#clean console
#rm(list=ls())

#OPTIONS two decimals and no scientific notation in numbers
options(digits=6,scipen=999)
defaultW <- getOption("warn")
options(warn = -1)

#FUNCTIONS
#Load utility functions
source(paste(directory,"/utilityFunctions.R", sep=""))

# THRESHOLDS that can be used to define rho
thresholds3SDList<-apply(datasets[[baselineValue]],2,function(x){mean(as.numeric(x))+3*sd(as.numeric(x))})

#create a fresh new file with the text results
if(file.exists(paste(experimentDir, "results.txt", sep=""))){file.remove(paste(experimentDir, "results_telecom.txt", sep=""))}

#compute CVR antipattern first
computeCVR <- function(serviceName,datasets,load, pi,rho,widthB,prop) {
    dataset <-
      as.data.frame(lapply(datasets[[load]], function(x) {
        as.numeric(as.character(x))
      }))
    lengExpIndex <- length(dataset$Time)
    #total no of buckets. ceiling is roundup. 
    #In this way, all the instants of time are considered and at most they are NA values that can be removed with na.rm in the quantile
    par <- ceiling(lengExpIndex / widthB)
    index <- which(colnames(dataset) == serviceName)
    
    s <- 0
    HPcount <- 0
    Bcount <- 0
    #par=number of buckets must be greater than 1
    for (k in 1:par) {
      #k-th bucket
      timeBucket <- dataset$Time[(s + 1):(s + widthB)]
      respTimeBucket <- dataset[(s + 1):(s + widthB), index]
      bucket <- data.frame(Time = timeBucket, respTime = respTimeBucket)
      scoreL <-
        computeInverse(datasets, load, s + 1, s + widthB, index, pi, rho)
      #count the violating buckets
      if (!is.na(scoreL) && scoreL>=0) {
        Bcount <- Bcount + 1
      }
      s <- s + widthB
    }
    return(score(Bcount, par * prop))
  }

computeTJ<- function(serviceName,datasets, r){
  #services<-names(datasets[[1]])[-1]
  loads<-names(datasets)[-1]
  index<-which(names(datasets[[1]])==serviceName)
  data1<-c()
  #to get the dataframe for the specific service
  for (i in loads){
    j<-which(loads==i)
    data1[j]<-datasets[[j]][index]
  }
  data2<-as.data.frame(data1, colnames=loads)
  colnames(data2)<-loads
 
  means<-c(mean(as.numeric(data2[,1])), mean(as.numeric(data2[,2])), 
       mean(as.numeric(data2[,3])), mean(as.numeric(data2[,4])), mean(as.numeric(data2[,5])), mean(as.numeric(data2[,6])))
  loads_num<-as.numeric(loads)
  rt<-data.frame(loads_num,means)
  predict_rt<- lm(means~loads_num+1,data=rt)
  scoreTJ<-score(as.numeric(coef(predict_rt)[2]),r)
  return(scoreTJ)
}

#To use the datset of Ericsson, uncomment this line
#datasets<-processedDatasets

# Detect TJ pattern

#Change Load to char to identify datasets lists in the below functions
load <- as.character(load)
#Detect the service name
index<-which(names(datasets[[1]])==serviceName)
#Check the performance Problem
lengthExp <- length(datasets[[1]]$Time)
#set the threshold. Change to 1 sec for Wert
rho<-thresholds3SDList[index]
scorePP<-computeInverse(datasets, load, 0, lengthExp, index, pi, rho)
#Check CVR
scoreCVR<-computeCVR(serviceName, datasets, load, pi, rho, widthB, prop)[1]
cat("The duration of the bucket is: ", widthB*5," sec and the proportion of buckets must be: ", prop, "\n", sep="")
#check TJ over loads
scoreTJ<-computeTJ(serviceName,datasets,r)
#Return the score PP and CVR an d TJ
cat("PP score= ", as.numeric(scorePP), "CVR score= ", as.numeric(scoreCVR),"TJ score ", as.numeric(scoreTJ), sep="\n")
