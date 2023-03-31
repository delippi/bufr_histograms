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
fig, (axl) = plt.subplots(1,1,sharey=False,sharex=True,figsize=(12,8),tight_layout=True)
fig_title_fontsize=15
sub_title_fontsize=13
xy_label_fontsize=13
tick_label_fontsize=10

try:
   date1=sys.argv[1]
   date2=sys.argv[2]
   tstamp=str(sys.argv[3])
   cdump=str(sys.argv[4])
   bufr_list=sys.argv[5:]
except:
   date1="2020032200"
   date2="2020032200"
   bufr_list=['1bamua']

#CREATE THE BINS
if(cdump=="OW"):
  bint=2/60.; bmin=-1.00; bmax=1.00+bint
  hrly=1
if(cdump=="GFS"):
  bint=15/60.; bmin=-4.00; bmax=4.00+bint
  hrly=6
bins=np.arange(bmin,bmax,bint)
xtick_labels = [str(int(round(i*60.))) for i in bins]
plt.xticks(bins,xtick_labels)
for tick in axl.get_xticklabels(): #format x labels
    tick.set_rotation(90)
    plt.setp(tick,visible=True,fontsize=tick_label_fontsize)
for tick in axl.get_yticklabels(): #format y labels
    plt.setp(tick,visible=True,fontsize=tick_label_fontsize)
xmid=np.arange( (bmin+bint)/2.00, (bmax+bmax+bint)/2.00,bint)


dates = dateutils.daterange(date1,date2,hrly)
print("dates: %s" % (dates))
print("bufr_list: %s" % (bufr_list))

scyc=[]
for scycl in dates:
   scyc.append(scycl[8:])
title="Data Receipt (%s-%s)"%(date1,date2)
colors=histogram_tools.large_color_scheme_54()

axl.axvline(0,color='k',linewidth=1)
if(cdump=="OW"):
  axl.axvline(26/60.,color='k',linewidth=1)   #0:26hr
  axl.axvline(-34/60.,color='k',linewidth=1)  #0:34hr
if(cdump=="GFS"):
  axl.axvline(165/60.,color='k',linewidth=1)  #2:45hr
  axl.axvline(-180/60.,color='k',linewidth=1) #3:00hr

def plot(dhrs,bufr,ibufr):
  dhrs=dhrs
  n_x,x,_ = axl.hist(dhrs,bins=bins,histtype='step',alpha=0.0)
  bin_centers = 0.5*(x[1:]+x[:-1])
  n_x=histogram_tools.replace_zero_with_nan(n_x)
  count=str(int(np.sum(histogram_tools.replace_nan_with_zero(n_x))))
  axl.plot(bin_centers,n_x,marker="o",markersize=6,color=colors[ibufr],linewidth=3,linestyle='-',label="%s (%s)"%(bufr,count) )
  n_x=histogram_tools.replace_nan_with_zero(n_x)
  print(np.sum(n_x))
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
    print("%s: present"%(bufr))
  except:
    print("%s: NA"%(bufr))
    exit()
    continue

axl.set_xlabel("Receipt (min)",fontsize=xy_label_fontsize)
axl.set_ylabel("Number of Observations",fontsize=xy_label_fontsize)
fig.suptitle(title,fontsize=fig_title_fontsize,y=0.98)
plt.title(title,fontsize=fig_title_fontsize,y=1.01,color='white')
fig.tight_layout(rect=[0,0.03,1,0.95])

axl.legend(loc='upper right',ncol=2)
axl.grid(color="white",linestyle='-', linewidth=1.)
plt.savefig('../figs/%s_%s-%s.png'%("receipt",str(date1),str(date2)))
toc=timer()
time=toc-tic
hrs=int(time/3600)
mins=int(time%3600/60)
secs=int(time%3600%60)
print("Total elapsed time: "+str(hrs).zfill(2)+":"+str(mins).zfill(2)+":"+str(secs).zfill(2))
