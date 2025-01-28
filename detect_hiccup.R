#install.packages("testthat", repos = "http://cran.us.r-project.org")
#press Cmd/Ctrl + Shift + T (or run devtools::test() if not) to run all the tests in a package
library(testthat)
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
  stop("Usage: Rscript detect_hiccup.R <serviceName> <load> <pi> <propTime> <widthB>", call.=FALSE)
} else {
  serviceName <- args[1]
  load <- as.character(args[2])
  pi <- as.numeric(args[3])
  propTime <- as.numeric(args[4])
  widthB <- as.numeric(args[5])
}

# serviceName: operation or microservice; string
# load: integer
# pi: 1 - tolerance percentile; real
# propTime: proportion of time expected; chi; real
# widthB: epsilon, size of a bucket; integer

# TEST input description to try as 
# Rscript detect_hiccup.R getCard 300 0.8525212134497199 0.5498185241756781 4
# serviceName <- "getCard"
# load <- '300'
# pi <- 0.8525212134497199
# propTime <- 0.5498185241756781
# widthB <- 4

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

# THRESHOLDS list that can be used to define rho
thresholds3SDList<-apply(datasets[[baselineValue]],2,function(x){mean(as.numeric(x))+3*sd(as.numeric(x))})

#compute the HP
computeHiccup<-function(datasets, index, load, widthB, lengthExp, pi, propTime, rho){
  dataset <- as.data.frame(lapply(datasets[[load]], function(x){as.numeric(as.character(x))}))
  #HPB_ms<-NULL
  #index <- which(colnames(dataset)==serviceName)
  #i <- index-1
  #rho <- thresholdList[index]
  s<-0
  HPcount<-0
  HpDuration<-NULL
  HpFinal<-list()
  #number of buckets
  par<-floor(lengthExp/widthB)
  for(k in 1:par){
    #k-th bucket
    timeBucket<-dataset$Time[(s+1):(s+widthB)]
    respTimeBucket<-dataset[(s+1):(s+widthB),index]
    bucket<-data.frame(Time=timeBucket,respTime=respTimeBucket)
    #Compute invRho and invPi in the bucket
    invValues<-computeInverse(datasets,load,s+1,s+widthB, index, pi, rho)
    #print(invValues)
    #cat("bucket no. =", k, "percentile of rho =", invValues[2], " pi =", pi, "\n", sep=" ")
    #check HP existence, store duration and count
    if(k!=par) {
      if (invValues > 0) {
        HpDuration <- c(HpDuration, timeBucket)
      } else{
        if (invValues <= 0 & !is.null(HpDuration)) {
          HpDuration <- c(HpDuration, timeBucket)
          HPcount <- HPcount + 1
          #print(HpDuration)
          HpFinal[[HPcount]] <- length(HpDuration)
          HpDuration <- NULL
        }
      }
    } else{
      #Last bucket
      if (!is.null(HpDuration)) {
        HpDuration <- c(HpDuration, tail(dataset$Time, lengthExp - par * widthB))
        HPcount <- HPcount + 1
        HpFinal[[HPcount]] <- length(HpDuration)
      }
    }
    s<-s+widthB
  }

  #compute the cumulative duration of a HP 
  cumulativeDurationHPs<-0
  if(HPcount==0){
    cat("Microservice ", colnames(dataset)[index], " does not contains hiccups", "\n", sep=" ")
  }else{
    #print(colnames(dataset)[index])
    #print(HPcount)
    for(j in 1:HPcount){
      #count the cumulative time of HPs
      cumulativeDurationHPs<-HpFinal[[j]]+cumulativeDurationHPs
    }
  }
#print(paste("cumulative duration with HP count= ", HPcount, " is ", cumulativeDurationHPs, sep=""))
return(score(lengthExp*propTime, cumulativeDurationHPs))
}


#Detect the service name
index<-which(names(datasets[[1]])==serviceName)
lengthExp <- length(datasets[[1]]$Time)
load <- as.character(load)
rho<-thresholds3SDList[index]
scorePP<-computeInverse(datasets, load, 0, lengthExp, index, pi, rho)
scoreAH <- computeHiccup(datasets, index, load, widthB, lengthExp, pi, propTime, rho)
cat("scorePP=", as.numeric(scorePP), "scoreAH=", as.numeric(scoreAH), sep="\n")


#TEST
#test_that("prova",{expect_gt(scorePP,0, label="PP")})
#test_that("prova",{expect_gt(scoreAH,0, label="AH")})

