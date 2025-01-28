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

# DEFINITION
# The Ramp is detected when the response time of an operation increases over time under constant Load.

# Thus, the heuristic will be
# Step 1: Check if there is a performance problem. FN: computeInverse() to compute the inverse of rho and compare it with the given parameter value pi
# Step 2: If 1 is true, check if the regression line exists (significance is not needed as we are not generalizing)  and if its slope is above a given threshold FN: computeRamp()

# args to call from Manager.py
args = commandArgs(trailingOnly=TRUE)
if (length(args) != 4) {
  stop("Usage: Rscript detect_ramp.R <serviceName> <load> <pi> <mu> ", call.=FALSE)
} else {
  serviceName <- args[1]
  load <- args[2]
  # percentage of non-violations of the threshold rho
  pi<-as.numeric(args[3])
  #threshold for the slope of the regression in the Ramp definition
  mu <- as.numeric(args[4])
}


#TEST data
# serviceName <- 'createOrder'
# load <- 300
# pi<-0.9
# mu<-0.000005

#Set your directory
setwd("~/Desktop")
#set code directory
directory <- file.path(paste(getwd(), "/GitHub/detection",sep=""), fsep = .Platform$file.sep)

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

computeRamp <- function(serviceName, datasets, load, mu) {
  #The RAMP antipattern with linear regression and significance
  #Linear regression strategy for the Ramp Wert pg. 181
  # or better for example the average for users=2 (per service). In this case use thresholdMList
  #head(dataset)
  dataset <- as.data.frame(lapply(datasets[[load]], function(x){as.numeric(as.character(x))}))
  index <- which(colnames(dataset)==serviceName)
  #i <- index-1

  #compute the slope of linear regression with significance. Only microservices with significant regression estimates are produced
  model<-NULL
  microservice<-as.numeric(dataset[,index])
  model<-lm(microservice ~  dataset$Time, data=faithful)
  
  pdf(file=paste(experimentDir, "/Picture/theRamp_",colnames(dataset)[index],".pdf", sep=""))
  plot(microservice~dataset$Time, type="p",pch="*", cex=1, xlab="Response Time", ylab=colnames(dataset)[index])
  abline(lm(microservice~dataset$Time))
  graphics.off()


  slope<-c()
  #COMPUTE THE SCORE TO detect the RAMP antipattern
  if(!is.null(model)){
    slope <- summary(model)$coefficients[2,1]
    print(serviceName) 
    print(slope)
    return(score(slope,mu))
  } else {
    return(NA)
  }
}

#Compute The Ramp

#To use the datset of Ericsson
#datasets<-processedDatasets

#Change Load to char to identify datasets lists in the below functions
load <- as.character(load)
index<-which(names(datasets[[1]])==serviceName)
#Check the perfoamnce Problem
lengthExp <- length(datasets[[1]]$Time)
#set the perforamnce threshold. Change it to 1 sec for wert
rho<-thresholds3SDList[index]
scorePP<-computeInverse(datasets, load, 0, lengthExp, index, pi, rho)[1]
scoreRP<-computeRamp(serviceName, datasets, load, mu)
cat("scorePP=", as.numeric(scorePP), "scoreRP=",as.numeric(scoreRP), sep="\n")
