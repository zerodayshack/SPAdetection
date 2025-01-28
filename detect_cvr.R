#Required libraries
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

# args to call from Manager.py
args = commandArgs(trailingOnly=TRUE)
if (length(args) != 5) {
  stop("Usage: Rscript detect_cvr.R <serviceName> <load> <pi> <prop> <widthB>", call.=FALSE)
} else {
  serviceName <- args[1]
  load <- as.character(args[2])
  pi <- as.numeric(args[3])
  prop <- as.numeric(args[4])
  widthB <- as.numeric(args[5])
}

#Test data
# serviceName <- "basket"
# load <- "300"
# pi <- 0.99
# prop <- 0.5
# widthB <- 5

#Set your directory
setwd("~/Desktop")
#set code directory
directory <- file.path(paste(getwd(), "/GitHub/detection",sep=""), fsep = .Platform$file.sep)
#clean console
#rm(list=ls())

#OPTIONS two decimals and no scientific notation
options(digits=6,scipen=999)
defaultW <- getOption("warn")
options(warn = -1)


#FUNCTIONS

#Load utility functions
source(paste(directory,"/utilityFunctions.R", sep=""))

baselineValue<-"2"
#LOADS
Loads<-c("50","100","150","200","250","300")
dataFile <- dir(paste(directory,"/datasets/", sep=""),  include.dirs=T, recursive = T)

#Read SockShop data either from pre-processed data
datasets<-list()
for(i in c(baselineValue,Loads)){
  if(dir.exists(paste(directory,"/datasets", sep=""))){
    filePath[i]<-dataFile[grep(paste("^","dataset_",i,"\\.", sep=""),dataFile)]
  }else{
    cat("check the existance of the datasets")
  }
  datasets[[i]]<-read.csv2(paste(directory,"/datasets/",filePath[i] ,sep=""))
}

# THRESHOLD that can be used to define rho
thresholds3SDList<-apply(datasets[[baselineValue]],2,function(x){mean(as.numeric(x))+3*sd(as.numeric(x))})

#compute CVR score
computeCVR <- function(serviceName,datasets,load, pi,rho,widthB,prop) {
    
    dataset <-
      as.data.frame(lapply(datasets[[load]], function(x) {
        as.numeric(as.character(x))
      }))
    lengExpIndex <- length(dataset$Time)
    #total no of buckets. ceiling is roundup. In this way all the instants of time are considered and at most they are NA values that can be removed with na.rm in the quantile
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
      scoreL <- computeInverse(datasets, load, s + 1, s + widthB, index, pi, rho)
      #print(paste(k, " ", scoreL, sep=""))
      #count the violating buckets
      if (!is.na(scoreL) && scoreL>=0) {
        Bcount <- Bcount + 1
      }
      s <- s + widthB
    }
    print(serviceName)
    print(Bcount)
    return(score(Bcount, par * prop))
  }

# PARAMETERS

#corresponding cumulative probability  (percentile) i.e. portion of requests that must
#not exceed the response time threshold per bucket
#pi <- 90/100 # continuous in [0.7, 0.95]

# minimum allowed proportion of violating buckets for CVR anti-pattern
#prop <- 0.5
#maximum allowed cumulative duration of hiccups for HP anti-pattern.if propTime =< prop
#then I cannot have both a HP and CVR pattern. Otherwise yes. This is bc how the HP is built.
#propTime <- 0.8  # continuous in [0.5, 0.9]
#findHICCUP Bucket strategy pg.396
#compute bucket width. 5 sec minimum
#A think time (i.e., the time between the completion of one HTTP request and the start of the next one)
#is added as negative exponential time  to represent the users’ real behaviour. Such time is executed between every two requests with 0, 1, and 5 seconds for minimum, mean, and maximum think time, respectively, and an allowed deviation of 5\% from the defined think time.
#meanInterReqTime<-1
#epsilon<-min(50*meanInterReqTime,5)

#FINAL COMPUTATION
#Detect the service name
index<-which(names(datasets[[1]])==serviceName)
#Check the performance Problem
lengthExp <- length(datasets[[1]]$Time)
#set the performance threshold. Change it to 1 sec for Wert
rho<-thresholds3SDList[index]

#print(rho)
load <- as.character(load)
scorePP<-computeInverse(datasets, load, 0, lengthExp, index, pi, rho)
#Check CVR
scoreCVR<-computeCVR(serviceName, datasets, load, pi, rho, widthB, prop)[1]
cat("The duration of the bucket is: ", widthB*5," sec and the proportion of buckets must be: ", prop, "\n", sep="")
#Return the score PP and CVR
cat("PP score ", as.numeric(scorePP), "CVR score ", as.numeric(scoreCVR), sep="\n")
