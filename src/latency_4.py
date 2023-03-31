from __future__ import print_function
from timeit import default_timer as timer
tic=timer()
import matplotlib
matplotlib.use("Agg")
from matplotlib import dates as mdates
import matplotlib.pyplot as plt
import ncepbufr
import pandas as pd
#import ncepy
import numpy as np
import sys
import datetime, dateutils
from datetime import datetime, timedelta 
import matplotlib.colors as mcolors
import os
import pdb
import gc
import histogram_tools
plt.style.use('ggplot')

plot_total=False

#SET UP THE FIGURE
fig, (axl,axr) = plt.subplots(1,2,sharey=False,sharex=True,figsize=(16,8),tight_layout=True)
#axr=plt.twinx()
fig_title_fontsize=15
sub_title_fontsize=13
xy_label_fontsize=13
tick_label_fontsize=10
#CREATE THE BINS
bint=0.25; bmin=0.00; bmax=8.00+bint
bint=0.25; bmin=0.00; bmax=6.00+bint
bins=np.arange(bmin,bmax,bint)
plt.xticks(bins)
for tick in axl.get_xticklabels(): #format x labels
    tick.set_rotation(90)
    plt.setp(tick,visible=True,fontsize=tick_label_fontsize)
for tick in axl.get_yticklabels(): #format y labels
    plt.setp(tick,visible=True,fontsize=tick_label_fontsize)
for tick in axr.get_xticklabels(): #format x labels
    tick.set_rotation(90)
    plt.setp(tick,visible=True,fontsize=tick_label_fontsize)
for tick in axr.get_yticklabels(): #format y labels
    plt.setp(tick,visible=True,fontsize=tick_label_fontsize)
xmid=np.arange( (bmin+bint)/2.00, (bmax+bmax+bint)/2.00,bint)

try:
   date1=sys.argv[1]
   date2=sys.argv[2]
   tstamp=str(sys.argv[3])
   bufr_list=sys.argv[4:]
except:
   date1="2020032200"
   date2="2020032200"
   bufr_list=['1bamua']

dates = dateutils.daterange(date1,date2,6)
print("dates: %s" % (dates))
print("bufr_list: %s" % (bufr_list))

scyc=[]
for scycl in dates:
   scyc.append(scycl[8:])
title="Data Latency (%s-%s)"%(date1,date2)
colors=histogram_tools.large_color_scheme_54()

#axr.axvline(xmid[3],color='k',linewidth=1)
axr.axvline(xmid[13],color='k',linewidth=1)
axr.axvline(xmid[10],color='k',linewidth=1)
#ADD PERCENTAGE LINE TO PLOT - right axis
def plot_perc(dhrs,n_all,color,xmid,typ):
  print(n_all)
  percent1=np.sum(n_all[0:4])/dhrs*100.
  if(np.isnan(percent1)):
    percent1=0
  percent3p5=np.sum(n_all[0:14])/dhrs*100.
  if(np.isnan(percent3p5)):
    percent3p5=0
  percent2p75=np.sum(n_all[0:11])/dhrs*100.
  if(np.isnan(percent2p75)):
    percent2p75=0

  print(dhrs,n_all[2],percent1,percent3p5,typ)  #04: <=1.0hrs
  perc=[]
  tot=0
  for j in n_all:
     tot=tot+j
     p=(tot/dhrs)*100
     perc.append(p)
  perc=np.array(perc)
  xmid=xmid[:-1] #remove last so the len is correct size
  if(typ == 'total' and plot_total):
    axr.plot(xmid,perc,color=color,marker="o",markersize=4,linewidth=0.5,linestyle='--',label="%s"%(typ))
  else:
     axr.plot(xmid,perc,color=color,marker="o",markersize=6,linewidth=1.5,linestyle='--',label="%s (%d%s)"%(typ,int(percent1),"%"))
  axr.set_ylabel("Percent Received",fontsize=xy_label_fontsize)
  axr.set_ylim([0,125])
  return percent1,percent2p75,percent3p5

def plot(dhrs,bufr,ibufr):
  dhrs=dhrs
  n_x,x,_ = axl.hist(dhrs,bins=bins,histtype='step',alpha=0.0)
  bin_centers = 0.5*(x[1:]+x[:-1])
  n_x=histogram_tools.replace_zero_with_nan(n_x)
  axl.plot(bin_centers,n_x,marker="o",markersize=6,color=colors[ibufr],linewidth=3,linestyle='-',label=bufr)
  n_x=histogram_tools.replace_nan_with_zero(n_x)
  return n_x,x,_,bin_centers

#############################################################
ibufr=-1
for bufr in bufr_list:
  ibufr+=1
  dhrs_x=np.empty((0),int)
  dhrs=[]
  n_xs=[]
  dhrs_len=0
  for date in dates:
    #print("%s" %(str(date)))
    try:
      data=np.load("%s.%s.npy"%(str(bufr),str(date)))
    except:
      break
    dhrs_x=np.append(dhrs_x,data,axis=0)
    dhrs_len=dhrs_len+len(dhrs_x)
  dhrs.append(dhrs_x)
  try:
    n_x,x,_,bin_centers = plot(dhrs[0],bufr,ibufr)
    n_xs.append(n_x)
    perc1,perc2p75,perc3p5=plot_perc(len(dhrs[0]),n_xs[0],colors[ibufr],xmid,str(bufr))
    f=open('perc.txt','a')
    f.write('%s %.3f %.3f\n'%(bufr,perc1,perc3p5))
    f.close()
    print("%s: present"%(bufr))
  except:
    print("%s: NA"%(bufr))
    exit()
    continue

axl.set_xlabel("Latency (hrs)",fontsize=xy_label_fontsize)
axr.set_xlabel("Latency (hrs)",fontsize=xy_label_fontsize)
axl.set_ylabel("Number of Observations",fontsize=xy_label_fontsize)
axr.set_yticks(np.arange(0,110,10))
fig.suptitle(title,fontsize=fig_title_fontsize,y=0.98)
plt.title(title,fontsize=fig_title_fontsize,y=1.01,color='white')
fig.tight_layout(rect=[0,0.03,1,0.95])

axl.legend(loc='upper right',ncol=2)
axr.legend(loc='lower right',ncol=2)
#axl.set_yscale("log")
axl.grid(color="white",linestyle='-', linewidth=1.)
axr.grid(color="white",linestyle='--', linewidth=1.)
plt.savefig('../figs/%s_%s-%s.png'%("latency_4",str(date1),str(date2)))
toc=timer()
time=toc-tic
hrs=int(time/3600)
mins=int(time%3600/60)
secs=int(time%3600%60)
print("Total elapsed time: "+str(hrs).zfill(2)+":"+str(mins).zfill(2)+":"+str(secs).zfill(2))
