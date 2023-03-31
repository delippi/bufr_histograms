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

#SET UP THE FIGURE
fig, (axl,axr) = plt.subplots(1,2,sharey=False,sharex=True,figsize=(12,8),tight_layout=True)
#axr=plt.twinx()
fig_title_fontsize=15
sub_title_fontsize=13
xy_label_fontsize=13
tick_label_fontsize=10
#CREATE THE BINS
bint=0.25; bmin=0.00; bmax=8.00+bint
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
except:
   date1="2020032200"
   date2="2020032200"

dates = dateutils.daterange(date1,date2,6)
print("dates: %s" % (dates))

count=[]     #this is the count for the legend label
names=[]     #this is the name in the legend label
dhrs_sat=np.empty((0),int)
dhrs_air=np.empty((0),int)
dhrs_ins=np.empty((0),int)
dhrs_gps=np.empty((0),int)
for date in dates:
  print("%s" %(str(date)))
  dhrs_sat=histogram_tools.load_data(dhrs_sat,"sat",date)
  dhrs_air=histogram_tools.load_data(dhrs_air,"air",date)
  dhrs_ins=histogram_tools.load_data(dhrs_ins,"ins",date)
  dhrs_gps=histogram_tools.load_data(dhrs_gps,"gps",date)

scyc=[]
for scycl in dates:
   scyc.append(scycl[8:])
title="Data Latency (%s-%s)"%(date1,date2)
colors=['#348ABD','#777777','#8EBA42','#E24A33'] #blue, gray, green, red

n_sat,x,_ = axl.hist(dhrs_sat,bins=bins,histtype='step',alpha=0.0)
bin_centers = 0.5*(x[1:]+x[:-1])
n_sat=histogram_tools.replace_zero_with_nan(n_sat)
axl.plot(bin_centers,n_sat,marker="o",markersize=6,color=colors[0],linewidth=3,linestyle='-',label='satellite')

n_air,x,_ = axl.hist(dhrs_air,bins=bins,histtype='step',alpha=0.0)
n_air=histogram_tools.replace_zero_with_nan(n_air)
axl.plot(bin_centers,n_air,marker="o",markersize=6,color=colors[1],linewidth=3,linestyle='-',label='aircraft')

n_ins,x,_ = axl.hist(dhrs_ins,bins=bins,histtype='step',alpha=0.0)
n_ins=histogram_tools.replace_zero_with_nan(n_ins)
axl.plot(bin_centers,n_ins,marker="o",markersize=6,color=colors[2],linewidth=3,linestyle='-',label='insitu')

n_gps,x,_ = axl.hist(dhrs_gps,bins=bins,histtype='step',alpha=0.0)
n_gps=histogram_tools.replace_zero_with_nan(n_gps)
axl.plot(bin_centers,n_gps,marker="o",markersize=6,color=colors[3],linewidth=3,linestyle='-',label='gps')

n_sat=histogram_tools.replace_nan_with_zero(n_sat)
n_air=histogram_tools.replace_nan_with_zero(n_air)
n_ins=histogram_tools.replace_nan_with_zero(n_ins)
n_gps=histogram_tools.replace_nan_with_zero(n_gps)

#ADD PERCENTAGE LINE TO PLOT - right axis
dhrs=len(dhrs_sat)+len(dhrs_air)+len(dhrs_ins)+len(dhrs_gps)
def plot_perc(dhrs,n_all,color,xmid,typ):
 print(dhrs,n_all[2],np.sum(n_all[0:4])/dhrs*100.,typ)
 perc=[]
 tot=0
 for j in n_all:
    tot=tot+j
    p=(tot/dhrs)*100
    perc.append(p)
 perc=np.array(perc)
 xmid=xmid[:-1] #remove last so the len is correct size
 if(typ == 'total'):
   axr.plot(xmid,perc,color=color,marker="o",markersize=4,linewidth=0.5,linestyle='--',label="%s"%(typ))
 else:
   axr.plot(xmid,perc,color=color,marker="o",markersize=6,linewidth=1.5,linestyle='--',label="%s"%(typ))
 axr.set_ylabel("Percent Received",fontsize=xy_label_fontsize)
 axr.set_ylim([0,125])

plot_perc(len(dhrs_sat),n_sat,colors[0],xmid,'satellite')
plot_perc(len(dhrs_air),n_air,colors[1],xmid,'aircraft')
plot_perc(len(dhrs_ins),n_ins,colors[2],xmid,'insitu')
plot_perc(len(dhrs_gps),n_gps,colors[3],xmid,'gps')

dhrs_tot=[dhrs_sat,dhrs_air,dhrs_ins,dhrs_gps]
flattened_list = [item for sublist in dhrs_tot for item in sublist] #this line can cause OOM errors
dhrs_tot=flattened_list
n_tot,x,_ = axl.hist(dhrs_tot,bins=bins,histtype='step',alpha=0.0)
n_tot=histogram_tools.replace_zero_with_nan(n_tot)
axl.plot(bin_centers,n_tot,marker="o",markersize=4,color='k',linewidth=1,linestyle='-',label='total')
n_tot=histogram_tools.replace_nan_with_zero(n_tot)
plot_perc(len(dhrs_tot),n_tot,'k',xmid,'total')# %s' % (str(len(dhrs_tot))))

axl.set_xlabel("Latency (hrs)",fontsize=xy_label_fontsize)
axr.set_xlabel("Latency (hrs)",fontsize=xy_label_fontsize)
axl.set_ylabel("Number of Observations",fontsize=xy_label_fontsize)
axr.set_yticks(np.arange(0,110,10))
fig.suptitle(title,fontsize=fig_title_fontsize,y=0.98)
plt.title(title,fontsize=fig_title_fontsize,y=1.01,color='white')
fig.tight_layout(rect=[0,0.03,1,0.95])

axl.legend()
axr.legend()
axl.set_yscale("log")
axl.grid(color="white",linestyle='-', linewidth=1.)
axr.grid(color="white",linestyle='--', linewidth=1.)
plt.savefig('../figs/latency_3_%s.png'%(tstamp))
toc=timer()
time=toc-tic
hrs=int(time/3600)
mins=int(time%3600/60)
secs=int(time%3600%60)
print("Total elapsed time: "+str(hrs).zfill(2)+":"+str(mins).zfill(2)+":"+str(secs).zfill(2))
plt.show()

