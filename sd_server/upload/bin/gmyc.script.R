#! /usr/bin/Rscript

#modified summary function to output to file.
summary.tofile <- function(object, file="", second.peak=FALSE, ...) {
	#res = result of GMYC
	#display summary of GMYC; likelihood values, chi-square test, estimated parameters, etc...
	
		if (second.peak==TRUE) {
		tmp<-table(cummax(object$likelihood))
		lik.peaks<-names(tmp[tmp>20])
		peak<-which(object$likelihood==lik.peaks[(length(lik.peaks)-1)])}

	
	cat("#Result of GMYC species delimitation\n", file=file)
	cat("\n\tmethod:\t", object[["method"]], sep="", file=file, append=TRUE)
	cat("\n\tlikelihood of null model:\t", object$likelihood[1], sep="", file=file, append=TRUE)
		if (second.peak==FALSE) {
			cat("\n\tmaximum likelihood of GMYC model:\t", max(object$likelihood), sep="", file=file, append=TRUE)
		} else 	{
			cat("\n\tmaximum likelihood of GMYC model:\t", object$likelihood[peak], sep="", file=file, append=TRUE)}
	
	#chisq test
	if (second.peak==FALSE) {
				LR <- 2*(max(object$likelihood)-object$likelihood[1])} else
				{LR <- 2*(object$likelihood[peak]-object$likelihood[1])}
	cat("\n\tlikelihood ratio:\t", LR, sep="", file=file, append=TRUE)

	pvalue <- 1-pchisq(LR, 2)	#revised chisq test
	
	cat("\n\tresult of LR test:\t", pvalue, ifelse(pvalue<0.001, "***", ifelse(pvalue<0.01, "**", ifelse(pvalue<0.05, "*", "n.s."))), sep="", file=file, append=TRUE)
	
		if (second.peak==FALSE) {
	cat("\n\n\tnumber of ML clusters:\t", object$cluster[which.max(object$likelihood)], sep="", file=file, append=TRUE)
		tmp<-object$cluster[object$likelihood>(max(object$likelihood)-2)]
		cat("\n\tconfidence interval:\t", paste(min(tmp),max(tmp),sep="-"), sep="", file=file, append=TRUE)
	cat("\n\n\tnumber of ML entities:\t", object$entity[which.max(object$likelihood)], sep="", file=file, append=TRUE)
		tmp<-object$entity[object$likelihood>(max(object$likelihood)-2)]
		cat("\n\tconfidence interval:\t", paste(min(tmp),max(tmp),sep="-"), sep="", file=file, append=TRUE)

	if (object[["method"]] == "single") {	
		cat("\n\n\tthreshold time:\t", object$threshold.time[which.max(object$likelihood)], "\n", sep="", file=file, append=TRUE)
	} else if (object[["method"]] == "multiple" || object[["method"]] == "exhaustive") {
		cat("\n\n\tthreshold time:\t", object$threshold.time[[which.max(object$likelihood)]], "\n", sep=" ", file=file, append=TRUE)
	}	
	cat("\n", file=file, append=TRUE)} else
	
	{cat("\n\n\tnumber of ML clusters:\t", object$cluster[peak], sep="", file=file, append=TRUE)
	cat("\n\tnumber of ML entities:\t", object$entity[peak], sep="", file=file, append=TRUE)
	if (object[["method"]] == "single") {	
		cat("\n\tthreshold time:\t", object$threshold.time[peak], "\n", sep="", file=file, append=TRUE)
	} else if (object[["method"]] == "multiple" || object[["method"]] == "exhaustive") {
		cat("\n\tthreshold time:\t", object$threshold.time[[peak]], "\n", sep=" ", file=file, append=TRUE)
	}	
	cat("\n", file=file, append=TRUE)}
}

#run gmyc from command line
ARGS <- commandArgs(trailingOnly=TRUE)

library(splits)

if (regexpr("\\.tre$", ARGS[1]) != -1) {
	tr <- read.tree(ARGS[1])
} else if (regexpr("\\.nex$", ARGS[1]) != -1) {
	tr <- read.nexus(ARGS[1])
}

gmycres <- gmyc(tr, method=ifelse(is.na(ARGS[2]), "single", ARGS[2]))

summary.tofile(gmycres, file=paste(ARGS[1], "summary", sep="_"))
write.table(spec.list(gmycres), paste(ARGS[1], "list", sep="_"), quote=F, sep="\t", row.names=F)

#plot to pdf
pdf(h=21, w=7, file=paste(ARGS[1], "plot.pdf", sep="_")) 
par(mfrow=c(3,1))
plot(gmycres)
dev.off()

#plot to png (21*7 inches, 300ppi)
png(h=21, w=7, units="in", res=300, file=paste(ARGS[1], "plot.png", sep="_")) 
par(mfrow=c(3,1))
plot(gmycres)
dev.off()




