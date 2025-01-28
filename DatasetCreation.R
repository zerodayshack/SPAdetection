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

#To create datasets in csv format from SockShop detail.xan file 

# args = commandArgs(trailingOnly=TRUE)
# if (length(args) != 1) {
#   stop("the directory path has not been inserted", call.=FALSE)
# } else {
#   directory <- args[1]
# }
directory<-"/Users/babsi/Desktop/GitHub/detection/"
  
#Set patterns to search file
experimentDirectory<-paste(directory, "Experiments/SockShop/", sep="")
dataPattern<-"detail.xan"
dataFileList <- dir(experimentDirectory, pattern = dataPattern, include.dirs=T, recursive = T)

#Read experiments' configuration file. This file contains the list of folders created from SockShop execution.
configurationFileName<-"LinkToExperiments.txt"
g<-read.csv(paste(experimentDirectory,"/",configurationFileName, sep=""))

#Find the name of the dataset files in configuration file
pattern<-c()
#LOADS
Loads<-c("50","100","150","200","250","300")
#Search for the name of the experiment
for(i in Loads){
  pattern[i]<-str_split(g[,],"\t")[[which(lapply(str_split(g[,],"\t"),function(x){which(x ==as.character(i))})!=0)]][6]
}

#search the file with BASELINE value "2" default.
baselineValue<-"2"
thresholdPattern<-str_split(g[,],"\t")[[which(lapply(str_split(g[,],"\t"),function(x){which(x ==as.character(baselineValue))})!=0)]][5]
pattern<-c(thresholdPattern,pattern)
names(pattern)[1]<-baselineValue

#List files.xan
dataFileList <- dir(experimentDirectory, pattern = dataPattern, include.dirs=T, recursive = T)
#create file paths. "2" is the baseline.
setwd("~")
setwd(directory)
filePath<-c()
for(i in c(baselineValue,Loads)){
  filePath[i]<-dataFileList[grep(paste("^",pattern[i], sep=""),dataFileList)]
}
source(paste(directory, "utilityFunctions.R",sep=""))
#create the list of datasets of Time +services each for one Load. Use preprocessData function in utilityFunctions.R
dir.create(paste(directory,"/datasets", sep=""))
datasets<-list()
for(i in c(baselineValue,Loads)){
  datasets[[i]]<-preprocessData(experimentDirectory,pattern[i],dataFileList)
  write.csv2(datasets[[i]],paste(directory,"/datasets/dataset_",i,".csv", sep=""),row.names = FALSE)
}
