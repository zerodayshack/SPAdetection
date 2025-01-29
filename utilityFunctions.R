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
#use library patchwork to combine multiple plots in one figure
#install.packages("patchwork")

#Create the datasets

#read dataset files and split into chunks of measurements according to Faban output. Identify "4th" element as Response Time.
preprocessData<-function(experimentDir, pattern, dataFileList){
  filePath<-dataFileList[grep(paste("^","Experiments/SockShop/",pattern, sep=""),dataFileList)]
  datasetTemp<-readLines(paste(experimentDir,"/",filePath, sep=""))
  t<-"Section:"
  factors<-grep(t,datasetTemp)
  datasetFF <-as.data.frame(split(datasetTemp, cumsum(1:length(datasetTemp) %in% factors))[[4]])
  
  #print(datasetFF[[1]][1])
  
  datasetFF<-datasetFF[-c(1:2,4),]
  headers<-unlist(strsplit(str_replace_all(datasetFF[1],"\\p{WHITE_SPACE}+", ","), ","))[-2]
  datasetF<-datasetFF[-1]
  out<-str_split(unlist(lapply(datasetF,function(x){str_replace_all(x, "\\p{WHITE_SPACE}+", ",")})), ",")[-c(374,375)]
  temp<-NULL
  for(i in 1:20){
    temp<-cbind(temp,sapply(out, "[", i))
  }
  colnames(temp)<-headers
  temp<-as.data.frame(temp)
  temp<-temp[-c(1:12),]
  temp$Time<-as.numeric(as.character(temp$Time))-60
  return(temp)
}

#Prepare the dataset from Ericcsson data. It uses the datasetGeneral formed in dataPreProcessing.R
preprocessDataEricsson<-function(datasetGT){
  tempr<-split(datasetGT,datasetGT$Load)
  return(tempr)
  }

# For ericsson only. reformatting the dataset. Now it has all operations as columns
reformattingDataset<- function(datasetGeneralTemp){
  require(dplyr)
  prova<-reshape(datasetGeneralTemp[,c(1:4,15)], idvar=c("instance","timestamp"), timevar=c("counter_name"), direction="wide") 
  prova1<-prova[,-c(6,8,10,12,14,16,18,20,22,24,26,27,28)]
  occ<-prova[,c(4,6,8,10,12,14,16,18,20,22,24,26)]
  #join the load columns to get one colum for Load
  mycol<-occ$load.Adjustment
  for(i in c(1:12)){
    occ1<-occ %>% mutate(mycol = coalesce(occ$mycol,occ[[i]]))
    occ<-occ1
  }
  prova1$load.Adjustment<-occ$mycol
  names(prova1)<-lapply(names(prova1), function(x){t<-gsub("response_time_average.","",x) })
  prova2<-prova1[,-c(1)]
  names(prova2)<-c("Time", "Adjustment","Load","Enquiry","DBDataManagement","Interrogation",
                           "Control","InternalCommunication","StatusUpdates","Offline","Online",
                           "Recompose","ResourcesRead","ResourcesUpdate")
  prova3<-prova2 %>% relocate('Load', .before='Adjustment')
  datasetGT<-prova3[c(1:ncol(prova3))]
  return (datasetGT)
}

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
#For ericcsson as load is not relevant
computeInverseE<-function(datasets, t_ini, t_end, index, pi, rho){
  dataset <- as.data.frame(lapply(datasets, function(x){as.numeric(as.character(x))}))
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
    pdf(file=paste(experimentDir, "/Picture/cumProb_",colnames(dataset)[index],".pdf", sep=""))
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

#PLOT response time over time per service. Saved in Picture/Ericsson/
distributionPlot<-function(bucket, rho){
  plot(bucket)
  invRho<-ecdf(bucket[,2])(rho)
  segments(0,rho,max(bucket$Time),rho,lty=3, col="red")
  text(0,rho,bquote(rho), col="red")
  segments(rho,invRho,0,invRho,lty=3)
}
myPlotAll<-function(datasets,thresholds3SDList, pi){
  services<-names(datasets %>% dplyr::select(-c(1,2)))
for (serviceName in services){
  dataset<-datasets %>% dplyr::select(Time, serviceName)
  rho<-thresholds3SDList[[serviceName]]
  pdf(file=paste(experimentDir, "/Picture/Ericsson/E_distributionsOverTime_",colnames(dataset)[2],".pdf", sep=""))
  distributionPlot(dataset, rho)
  graphics.off()
  pdf(file=paste(experimentDir, "/Picture/Ericsson/E_Cumdistribution_",colnames(dataset)[2],".pdf", sep=""))
  myPlotCumDist(dataset, rho,pi)
  graphics.off()
}}
