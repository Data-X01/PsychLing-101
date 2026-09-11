library(data.table)
library(ggplot2)
library(Hmisc)
library(lmerTest)

bbar <- function(plotdat) {
    n<-names(plotdat)
    len<-length(n)
    y<-n[len]
    x<-n[1]
    plotSummary <- summarySE(plotdat,measurevar=y,groupvars=n[1:len-1],na.rm=TRUE)
    if (len > 2) { 
        group<-n[2] 
        plot <- ggplot(plotSummary,aes(y=get(y),x=get(x),fill=get(group)),environment=environment()) + geom_bar(stat="identity",position="dodge") + scale_fill_discrete(name=group)
    }
    else {
        plot <- ggplot(plotSummary,aes(y=get(y),x=get(x)),environment=environment()) + geom_bar(stat="identity")
    }
    plot <- plot + xlab(x) + ylab(y)
    plot <- plot + geom_errorbar(width=.1, aes(ymin=get(y)-se, ymax=get(y)+se),position=position_dodge(.9))
    plot
}

bline <- function(plotdat) {
    n<-names(plotdat)
    len<-length(n)
    y<-n[len]
    x<-n[1]
    plotSummary <- summarySE(plotdat,measurevar=y,groupvars=n[1:len-1],na.rm=TRUE)
    if (len == 4) { 
        group<-n[2] 
        linetype<-n[3]
        plot <- ggplot(plotSummary,aes(y=get(y),x=get(x),color=get(group),linetype=get(linetype)),environment=environment()) + geom_line(stat="identity")
    }
    if (len == 3) { 
        group<-n[2] 
        plot <- ggplot(plotSummary,aes(y=get(y),x=get(x),color=get(group),group=get(group)),environment=environment()) + geom_line(stat="identity")
    }
    else {
        plot <- ggplot(plotSummary,aes(y=get(y),x=get(x),group=1),environment=environment()) + geom_line(stat="identity",size=1)
    }
    plot <- plot + xlab(x) + ylab(y) + geom_point(size=3)
    #plot <- plot + geom_errorbar(width=.1, aes(ymin=get(y)-se, ymax=get(y)+se),position=position_dodge(.9))
    plot
}



handcoded <- fread('wrap_coded_20190618.csv')
snafu <- fread('clusters.csv')
mci_diagnosis <- fread('jcz_mci_diagnosis_20190906.csv')
demographics <- fread('demographics20190817.csv')

setkey(snafu, id, listnum)
setkey(handcoded, id, listnum)
setkey(mci_diagnosis, id, listnum)
setkey(demographics,id)

dat<-merge(snafu,handcoded)
dat<-merge(dat,mci_diagnosis)
dat<-merge(dat,demographics)

# average age at first visit
dat[,minlist:=min(listnum),keyby=id]
dat[listnum==minlist,mean(curage)]

# hand-coded cluster sizes were calculated slightly differently than SNAFU
dat[,animSemMean := animSemMean + 1]
    
# percentage of MCI visits -- old MCI file
sum(dat[aMCI_vis!=9,aMCI_vis])/nrow(dat)
sum(dat[naMCI_vis!=9,naMCI_vis])/nrow(dat)

# gender breakdown
table(dat[,gender])

# replace edyrs variable with max20 variable
dat[,edyrs:=`EdYears_Coded_Max20`]

# number of lists where total # of responses dont match up
dat[numresponses==(animTotRaw+animTotRep+animTotErr),.N]
# off by one
sum(dat[,abs(numresponses-(animTotRaw+animTotRep+animTotErr))==1])

# num responses correlation + rmse
numresponses_outlier_cutoff <- dat[,mean(numresponses)]+3*(dat[,sd(numresponses)])
num_numresponses_outliers <- nrow(dat[numresponses>=numresponses_outlier_cutoff])
rcorr(dat[numresponses<numresponses_outlier_cutoff,numresponses],dat[numresponses<numresponses_outlier_cutoff,(animTotRaw+animTotRep+animTotErr)])
dat[numresponses<numresponses_outlier_cutoff,sqrt(mean((numresponses-(animTotRaw+animTotRep+animTotErr))^2))]

# perseverations correlation + rmse + table
perseveration_outlier_cutoff <- dat[,mean(animTotRep)]+3*(dat[,sd(animTotRep)])
num_perseveration_outliers <- nrow(dat[animTotRep>=perseveration_outlier_cutoff])
rcorr(dat[animTotRep<perseveration_outlier_cutoff,animTotRep],dat[animTotRep<perseveration_outlier_cutoff,perseverations])
dat[animTotRep<perseveration_outlier_cutoff,sqrt(mean((perseverations-animTotRep)^2))]
table(dat[,.(perseverations,animTotRep)])

# cluster switch analysis, 999 = missing data
switch_outlier_cutoff <- dat[animSemSwi!=999,mean(animSemSwi)]+3*(dat[animSemSwi!=999,sd(animSemSwi)])
num_switch_outliers <- nrow(dat[animSemSwi>=switch_outlier_cutoff]) - nrow(dat[animSemSwi==999])
rcorr(dat[animSemSwi<switch_outlier_cutoff,animSemSwi],dat[animSemSwi<switch_outlier_cutoff,clusterswitch])
dat[animSemSwi<switch_outlier_cutoff,sqrt(mean((animSemSwi-clusterswitch)^2))]

# cluster size analysis, 1000 = missing data, 140 = coding error?
clustersize_outlier_cutoff <- dat[animSemMean!=1000 & animSemMean!=140,mean(animSemMean)]+3*(dat[animSemMean!=1000 & animSemMean!=140,sd(animSemMean)])
num_clustersize_outliers <- nrow(dat[animSemMean>=clustersize_outlier_cutoff]) - nrow(dat[animSemMean==999 | animSemMean==140])
rcorr(dat[animSemMean<clustersize_outlier_cutoff,animSemMean],dat[animSemMean<clustersize_outlier_cutoff,clustersize])
dat[animSemMean<clustersize_outlier_cutoff,sqrt(mean((clustersize-animSemMean)^2))]


# intrusions
intrusion_outlier_cutoff<-dat[,mean(animTotErr)]+3*(dat[,sd(animTotErr)])
num_intrusion_outliers <- nrow(dat[animTotErr>=intrusion_outlier_cutoff])
rcorr(dat[animTotErr<intrusion_outlier_cutoff,animTotErr],dat[animTotErr<intrusion_outlier_cutoff,intrusions])
dat[animTotErr<intrusion_outlier_cutoff,sqrt(mean((animTotErr-intrusions)^2))]

# mci binary variable -- 34 mci and 841 normal
#mcidat <- dat [consensus_dx=="Clinical_MCI" | consensus_dx=="Cognitvely_Normal"]
mcidat <- dat [aMCI_vis != 9]

# age sig both, interaction marginal for snafu
# without interaction, all sig
summary(lmer(animTotRaw ~ curage * aMCI_vis + (1|id),data=mcidat[animTotRaw<numresponses_outlier_cutoff]))
summary(lmer(numresponses ~ curage * aMCI_vis + (1|id),data=mcidat[animTotRaw<numresponses_outlier_cutoff]))

# age only for all
summary(lmer(animSemSwi ~ curage * aMCI_vis + (1|id),data=mcidat[animSemSwi<switch_outlier_cutoff]))
summary(lmer(clusterswitch ~ curage * aMCI_vis + (1|id),data=mcidat[animSemSwi<switch_outlier_cutoff]))

# 
summary(lmer(animSemMean ~ curage * aMCI_vis + (1|id),data=mcidat[animSemMean<clustersize_outlier_cutoff]))
summary(lmer(clustersize ~ curage * aMCI_vis + (1|id),data=mcidat[animSemMean<clustersize_outlier_cutoff]))

# 
summary(lmer(animTotErr ~ curage * aMCI_vis + (1|id),data=mcidat[animTotErr<intrusion_outlier_cutoff]))
summary(lmer(intrusions ~ curage * aMCI_vis + (1|id),data=mcidat[animTotErr<intrusion_outlier_cutoff]))

# 
summary(lmer(animTotRep ~ curage * aMCI_vis + (1|id),data=mcidat[animTotRep<perseveration_outlier_cutoff]))
summary(lmer(perseverations ~ curage * aMCI_vis + (1|id),data=mcidat[animTotRep<perseveration_outlier_cutoff]))

# 
summary(lmer(wordfreq ~ curage * aMCI_vis + (1|id),data=mcidat))
summary(lmer(aoa ~ curage * aMCI_vis + (1|id),data=mcidat))

library(gridExtra)
library(Rmisc)

mcidat[,Age:="Older"]
mcidat[curage<=median(curage),Age:="Younger"]
mcidat[,mci_status:="Healthy"]
mcidat[aMCI_vis==1,mci_status:="aMCI"]
mcidat[,Age:=factor(Age)]
mcidat[,mci_status:=factor(mci_status)]
mcidat$Age <- factor(mcidat$Age, levels=c("Younger","Older"))
mcidat$mci_status <- factor(mcidat$mci_status, levels=c("Healthy","aMCI"))

# list num subj in each bin

g_legend <- function(a.gplot){ 
    tmp <- ggplot_gtable(ggplot_build(a.gplot))
    leg <- which(sapply(tmp$grobs, function(x) x$name) == "guide-box") 
    legend <- tmp$grobs[[leg]]
    legend
} 

leg <- g_legend(bbar(mcidat[aMCI_vis!=9 & animTotRaw<numresponses_outlier_cutoff,numresponses,.(mci_status,Age)])  + xlab("Cognitive Status") + ylab("Number of responses (SNAFU)") + theme_classic() + scale_y_continuous(limits = c(0,25), expand = c(0, 0))  + scale_fill_discrete(name="Age\n(median split)") + theme(legend.text=element_text(size=14), legend.title=element_text(size=14)))
#ggsave("legend.eps", legendeps)

# plot num responses
a <- bbar(mcidat[aMCI_vis!=9 & animTotRaw<numresponses_outlier_cutoff,animTotRaw,.(mci_status,Age)]) + xlab("Cognitive Status") + ylab("Number of responses (human coded)") + theme_classic() + scale_y_continuous(limits = c(0,25), expand = c(0, 0)) + theme(legend.position = "none", axis.text=element_text(size=14), axis.title=element_text(size=14))
b <- bbar(mcidat[aMCI_vis!=9 & animTotRaw<numresponses_outlier_cutoff,numresponses,.(mci_status,Age)])  + xlab("Cognitive Status") + ylab("Number of responses (SNAFU)") + theme_classic() + scale_y_continuous(limits = c(0,25), expand = c(0, 0)) + theme(legend.position = "none", axis.text=element_text(size=14), axis.title=element_text(size=14))
c <- arrangeGrob(a,b,leg,ncol=3, widths=c(3,3,1))

#grid.arrange(a,b,ncol=2)
ggsave("bar_numresponses.eps", c, width=9)

# plot cluster size
a <- bbar(mcidat[aMCI_vis!=9 & animSemMean<clustersize_outlier_cutoff,animSemMean,.(mci_status,Age)]) + xlab("Cognitive Status") + ylab("Average cluster size (human coded)") + theme_classic() + scale_y_continuous(limits = c(0,3), expand = c(0, 0)) + theme(legend.position = "none", axis.text=element_text(size=14), axis.title=element_text(size=14))
b <- bbar(mcidat[aMCI_vis!=9 & animSemMean<clustersize_outlier_cutoff,clustersize,.(mci_status,Age)]) + xlab("Cognitive Status") + ylab("Average cluster size (SNAFU)") + theme_classic() + scale_y_continuous(limits = c(0,3), expand = c(0, 0)) + theme(legend.position = "none", axis.text=element_text(size=14), axis.title=element_text(size=14))
c <- arrangeGrob(a,b,leg,ncol=3, widths=c(3,3,1))
#grid.arrange(a,b,ncol=2)
ggsave("bar_clustersize.eps", c, width=9)

# plot cluster switch
a <- bbar(mcidat[aMCI_vis!=9 & animSemSwi<switch_outlier_cutoff,animSemSwi,.(mci_status,Age)]) + xlab("Cognitive Status") + ylab("Number of cluster switches (human coded)") + theme_classic() + scale_y_continuous(limits = c(0,12.5), expand = c(0, 0)) + theme(legend.position = "none", axis.text=element_text(size=14), axis.title=element_text(size=14))
b <- bbar(mcidat[aMCI_vis!=9 & animSemSwi<switch_outlier_cutoff,clusterswitch,.(mci_status,Age)]) + xlab("Cognitive Status") + ylab("Number of cluster switches (SNAFU)") + theme_classic() + scale_y_continuous(limits = c(0,12.5), expand = c(0, 0)) + theme(legend.position = "none", axis.text=element_text(size=14), axis.title=element_text(size=14))
c <- arrangeGrob(a,b,leg,ncol=3, widths=c(3,3,1))
#grid.arrange(a,b,ncol=2)
ggsave("bar_clusterswitch.eps", c, width=9)

# word freq and age of acquisition
a <- bbar(mcidat[aMCI_vis!=9,wordfreq,.(mci_status,Age)]) + xlab("Cognitive Status") + ylab("Average word frequency (SNAFU)") + theme_classic() + scale_y_continuous(limits = c(0,25), expand = c(0, 0)) + theme(legend.position = "none", axis.text=element_text(size=14), axis.title=element_text(size=14))
b <- bbar(mcidat[aMCI_vis!=9,aoa,.(mci_status,Age)]) + xlab("Cognitive Status") + ylab("Average age of acquisition (SNAFU)") + scale_y_continuous(limits = c(0,6), expand = c(0, 0)) + theme_classic() + theme(legend.position = "none", axis.text=element_text(size=14), axis.title=element_text(size=14))
c <- arrangeGrob(a,b,leg,ncol=3, widths=c(3,3,1))
#grid.arrange(a,b,ncol=2)
ggsave("bar_wordfreq.eps", c, width=9)

# perseverations
a <- bbar(mcidat[aMCI_vis!=9 & animTotRep<perseveration_outlier_cutoff,animTotRep,.(mci_status,Age)]) + xlab("Cognitive Status") + ylab("Number of perseverations (human coded)") + theme_classic() + scale_y_continuous(limits = c(0,0.7), expand = c(0, 0)) + theme(legend.position = "none", axis.text=element_text(size=14), axis.title=element_text(size=14))
b <- bbar(mcidat[aMCI_vis!=9 & animTotRep<perseveration_outlier_cutoff,perseverations,.(mci_status,Age)]) + xlab("Cognitive Status") + ylab("Number of perseverations (SNAFU)") + theme_classic() + scale_y_continuous(limits = c(0,0.7), expand = c(0, 0)) + theme(legend.position = "none", axis.text=element_text(size=14), axis.title=element_text(size=14))
c <- arrangeGrob(a,b,leg,ncol=3, widths=c(3,3,1))
#grid.arrange(a,b,ncol=2)
ggsave("bar_perseverations.eps", c, width=9)


# intrusions
a <- bbar(mcidat[aMCI_vis!=9 & animTotErr<intrusion_outlier_cutoff,animTotErr,.(mci_status,Age)]) + xlab("Cognitive Status") + ylab("Number of intrusions (human coded)") + theme_classic() + scale_y_continuous(limits = c(0,0.45), expand = c(0, 0)) + theme(legend.position = "none", axis.text=element_text(size=14), axis.title=element_text(size=14))
b <- bbar(mcidat[aMCI_vis!=9 & animTotErr<intrusion_outlier_cutoff,intrusions,.(mci_status,Age)]) + xlab("Cognitive Status") + ylab("Number of intrusions (SNAFU)") + theme_classic() + scale_y_continuous(limits = c(0,0.45), expand = c(0, 0)) + theme(legend.position = "none", axis.text=element_text(size=14), axis.title=element_text(size=14))
c <- arrangeGrob(a,b,leg,ncol=3, widths=c(3,3,1))
#grid.arrange(a,b,ncol=2)
ggsave("bar_intrusions.eps", c, width=9)

