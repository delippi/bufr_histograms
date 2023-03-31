from __future__ import print_function
from timeit import default_timer as timer
tic=timer()
import matplotlib
#matplotlib.use("Agg")
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


thisdict=histogram_tools.bufr_dictionary() #see /home/dlippi/bin/python/histogram_tools.py

#PATH TO GDAS DATA
bufr_path1="/work/noaa/sfc-perts/gbates/hrlyda_dumps/6hrly/"
bufr_dump1="gdas"
bufr2_dump1="gdas"
##PATH TO GFS DATA
#bufr_path2="/work/noaa/sfc-perts/gbates/hrlyda_dumps/6hrly/"
#bufr_dump2="gfs"
#bufr2_dump2="gfs"
##PATH TO SHORT DATA
#bufr_path3="/work/noaa/sfc-perts/gbates/hrlyda_dumps/short/"
#bufr_dump3="gdas"
#bufr2_dump3="short"
##PATH TO LONG DATA
#bufr_path4="/work/noaa/sfc-perts/dlippi/hrlyda_dumps/long/"
#bufr_dump4="gdas"
#bufr2_dump4="long"

paths=[bufr_path1]
dumps=[bufr_dump1]
dumps2=[bufr2_dump1]
try:
   date1=sys.argv[1]
   date2=sys.argv[2]
   bufr_list=sys.argv[3:]
except:
   date1="2020032200"
   date2="2020032200"
   bufr_list=['1bamua']

dates = dateutils.daterange(date1,date2,1)
print("dates: %s" % (dates))

#HEADER STRING FOR NONPREPBUFR FILES
#hdstr="YEAR MNTH DAYS HOUR MINU"
hdstr="YEAR MNTH DAYS HOUR MINU RCYR RCMO RCDY RCHR RCMI"
#HEADER STRING FOR PREPBUFR FILES
hdstr_prep="DHR TYP RPT RCT"

yesRCT=0
noRCT=0
bad=0

nobs=0       #number of total observation count
time=[]      #list for storing dhrs
count=[]     #this is the count for the legend label
names=[]     #this is the name in the legend label
dhrs_sat=np.empty((0),int)
dhrs_air=np.empty((0),int)
dhrs_ins=np.empty((0),int)
dhrs_gps=np.empty((0),int)
for date in dates:
   colors=[]    #list of colors for the plot
   c=0          #variable for color list
   index=-1
   for path in paths:
      index = index + 1
      dump = dumps[index]  #gfs/gdas/gdas
      dump2= dumps2[index] #gfs/gdas/short
      
      for bufr in bufr_list:
            typ=thisdict[bufr]
            sat=False; air=False; ins=False; gps=False
            if(typ=="sat"): sat=True
            if(typ=="air"): air=True
            if(typ=="ins"): ins=True
            if(typ=="gps"): gps=True
            names.append("%s: %s" % (dump2,bufr))
            name="%s: %s" % (dump2,bufr)    #name
            pdy=date[:8] #cut the date to YYYYMMDD
            cyc=date[8:] #cut the date to CC
            nobs2=0
            
            numpy_filename="%s.%s" %(bufr,str(date))

            try:
              data=np.load("%s.npy"%(numpy_filename))
              print("%s (%s): %s, %s, %s" %(name,dump,str(date),typ,str(len(data))))
            except:
              print("%s (%s): %s, %s, NA" %(name,dump,str(date),typ))
              continue
            if(sat):
              dhrs_sat=np.append(dhrs_sat,data,axis=0)
            if(air):
              dhrs_air=np.append(dhrs_air,data,axis=0)
            if(ins):
              dhrs_ins=np.append(dhrs_ins,data,axis=0)
            if(gps):
              dhrs_gps=np.append(dhrs_gps,data,axis=0)
            del data 
            gc.collect()
   np.save("sat.%s"%(str(date)), dhrs_sat)
   np.save("air.%s"%(str(date)), dhrs_air)
   np.save("ins.%s"%(str(date)), dhrs_ins)
   np.save("gps.%s"%(str(date)), dhrs_gps)
