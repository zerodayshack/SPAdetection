#Define all functions needed for executing SPA detection in R
#Creates the datasets list that is used in the detect files

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
library(RColorBrewer)


#FUNCTIONS

#Create the datasets list in the R project. 
#Patterns must have character values
directory<-here::here()
Loads<-c("50","100","150","200","250","300")
baselineValue<-"2"
patterns<-c(baselineValue,Loads)
datasetsCreation<-function(directory,Loads,baselineValue){
  #Find csv files in project directory
  dataFileList <- dir(directory, pattern = ".csv", include.dirs=T, recursive = T)
  
  filePath<-c()
  for(i in 1:length(patterns)){
    #datasets are named with corresponding laod value in datasets forlder
    filePath[i]<-dataFileList[grep(paste(patterns[i],".", sep=""),fixed=TRUE,dataFileList)]
  }
  datasets<-list()
  for(i in patterns){
    k<-which(c(baselineValue,Loads)==i)
    datasets[[i]]<-read.csv(paste(directory,"/",filePath[k], sep=""), header=TRUE, sep=";")
  }
  return(datasets)
}
datasets<-datasetsCreation(directory,Loads,baselineValue)

#score for the pattern evaluation
score <- function(a, b) {
  return(a - b)
}

#compute the inverse according to the empirical sample distribution. 
#t_ini, t_end are the starting/ending positions in the $Time variable; index is the column in the dataset concerning 
#the service index must be greater than 1;  pi is the quantile for the empirical distribution; rho is the scalability threshold

computeInverse<-function(datasets, load, t_ini, t_end, index, pi, rho){
  dataset <- as.data.frame(lapply(datasets[[load]], function(x){as.numeric(as.character(x))}))
  timeBucket<-dataset$Time[t_ini:t_end]
  respTimeBucket<-dataset[t_ini:t_end,index]
  bucket<-data.frame(Time=timeBucket,respTime=respTimeBucket)
  #empirical cumulative distribution
  cumProb<-as.vector(unlist(lapply(bucket$respTime, function(x){ecdf(bucket$respTime)(x)})))
  #print(cumProb)
  invPi<-quantile(bucket$respTime,pi, na.rm=TRUE)
  invRho<-ecdf(bucket$respTime)(rho)
  
  #PLOTS
  if(t_ini==0 & t_end==length(dataset$Time)){
    #create a folder for the pictures if it does not exist yet
    dir.create(paste(directory, "/Picture/", sep=""))
    pdf(file=paste(directory, "/Picture/cumProb_",colnames(dataset)[index],".pdf", sep=""))
    plot(bucket$respTime,cumProb, type="p",pch="*", cex=1, xlab="Response Time", ylab="Cumulative probability")
    points(invPi,pi,  pch="*", cex=1.3, col="red")
    points(rho,invRho,  pch="*", cex=1.3, col="red")
    segments(0,pi, invPi,pi, lty=4)
    segments(invPi,pi,invPi,0, lty=4)
    text(0,pi,bquote(pi))
    segments(rho,0,rho,invRho,lty=3)
    segments(rho,invRho,0,invRho,lty=3)
    text(rho,0,bquote(rho))
    text(min(bucket$respTime)+0.0001,round(invRho,2)+0.015, round(invRho,2))
    text(round(invPi,4),min(cumProb), round(invPi,4))
    graphics.off()
  }
  #Returns the score used to check a performance problem
  scoreDiff<-c()
  scoreDiff<-score(pi,invRho)
  return(scoreDiff)
}

#To use it with buckets of Time and serviceName
computeInverseEE<-function(bucket,pi, rho){
 
  invRho<-ecdf(bucket[,2])(rho)
  
  #Returns the score used to check a performance problem
  scoreDiff<-c()
  scoreDiff<-score(pi,invRho)
  return(scoreDiff)
}

#PLOT of cum distribution
myPlotCumDist<-function(bucket, rho, pi){
  cumProb<-as.vector(unlist(lapply(bucket[,2], function(x){ecdf(bucket[,2])(x)})))
  invPi<-quantile(bucket[,2],pi, na.rm=TRUE)
  invRho<-ecdf(bucket[,2])(rho)
  plot(bucket[,2],cumProb, type="p",pch="*", cex=1, xlab="Response Time", ylab="Cumulative probability")
  points(invPi,pi,  pch="*", cex=1.3, col="red")
  points(rho,invRho,  pch="*", cex=1.3, col="red")
  segments(0,pi, invPi,pi, lty=4)
  segments(invPi,pi,invPi,0, lty=4)
  text(0,pi,bquote(pi))
  segments(rho,0,rho,invRho,lty=3)
  segments(rho,invRho,0,invRho,lty=3)
  text(rho,0,bquote(rho))
  text(min(bucket$respTime)+0.0001,round(invRho,2)+0.015, round(invRho,2))
  text(round(invPi,4),min(cumProb), round(invPi,4))
  }

