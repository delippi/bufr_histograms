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
import histogram_tools

thisdict=histogram_tools.bufr_dictionary() #see /home/dlippi/bin/python/histogram_tools.py

##################################################################################
#PATH TO GDAS DATA
bufr_path1="/work/noaa/sfc-perts/gbates/hrlyda_dumps/6hrly/" #filtered
#bufr_path1="/work/noaa/rstprod/dump/"                        #unfiltered
bufr_dump1="gdas"
bufr2_dump1="gdas"
#PATH TO GFS DATA
#bufr_path2="/work/noaa/sfc-perts/gbates/hrlyda_dumps/6hrly/"
bufr_path2="/work/noaa/fv3-cam/dlippi/hrlyda_dumps/gfs/"
bufr_dump2="gfs"
bufr2_dump2="gfs"
#PATH TO SHORT DATA
#bufr_path3="/work/noaa/sfc-perts/gbates/hrlyda_dumps/short/"
bufr_path3="/work/noaa/fv3-cam/dlippi/hrlyda_dumps/short/"
bufr_dump3="gdas"
bufr2_dump3="short"

#PATH TO LONG DATA
bufr_path4="/work/noaa/sfc-perts/dlippi/hrlyda_dumps/long/"
bufr_dump4="gdas"
bufr2_dump4="long"
#DONT FORGET TO UPDATE "ob_window"

paths=[bufr_path2]
dumps=[bufr_dump2]
dumps2=[bufr2_dump2]
try:
   date1=sys.argv[1]
   date2=sys.argv[2]
   cdump=sys.argv[3]
   bufr_list=sys.argv[4:]
except:
   date1="2020032200"
   date2="2020032200"
   bufr_list=['1bamua']

if(cdump=="OW"):
  hrly=1
if(cdump=="GFS"):
  hrly=6
dates = dateutils.daterange(date1,date2,hrly)
print("dates: %s" % (dates))
date=datetime.strptime(dates[0],'%Y%m%d%H')
left=date + timedelta(hours=-3,minutes=0)
right=date + timedelta(hours=3,minutes=0)
ob_window=[left,right]
rct_cutoff=date+timedelta(hours=5,minutes=0)
#############################################################################
#HEADER STRING FOR NONPREPBUFR FILES
#hdstr="YEAR MNTH DAYS HOUR MINU"
hdstr1="YEAR MNTH DAYS HOUR MINU"
hdstr2="RCYR RCMO RCDY RCHR RCMI"
#HEADER STRING FOR PREPBUFR FILES
#hdstr_prep="DHR TYP RPT RCT"

yesRCT=0
noRCT=[0,0]
bad=0
bad_obtime=0
bad_rctime=0
nobs=0       #number of total observation count
nsub=0
nhed=0
statgt0_count=0

##############################################################################################################
def check_receipt(dt,yesRCT,noRCT,nobs,nobs2): #the receipt time must be length 5 otherwise not all data is there
  if(len(dt)==5):
    dt,yesRCT,noRCT,nobs,nobs2,status=check_dates(dt,yesRCT,noRCT,nobs,nobs2)
  else:
    #print("\033[Kreceipt=%s" % (dt))
    dt=[2222,1,1,0,0] #year,month,day,hour,min; set ridiculous date for missing rct times
    noRCT[0]+=1
    status=1
  nobs+=1  #count total obs
  nobs2+=1 #count obs for each file separately
  return dt,yesRCT,noRCT,nobs,nobs2,status 


def check_dates(dt,yesRCT,noRCT,nobs,nobs2): #check the year, month, day not equal to zero
  status=0
  if(dt[0]*dt[1]*dt[2]==0):
    #print("\033[Kerror2: dt=%s" % (dt))
    dt=[2222,1,1,0,0] #year,month,day,hour,min; set ridiculous date for missing rct times
    noRCT[1]+=1
    status=1
  else:
    yesRCT+=1
  return dt,yesRCT,noRCT,nobs,nobs2,status

def compute_receipt(date,dt):
  #time_str="%s%s%s%s%s" % (t[0],str(t[1]).zfill(2),str(t[2]).zfill(2),str(t[3]).zfill(2),str(t[4]).zfill(2))
  da_time=date
  da_time=datetime.strptime(date,'%Y%m%d%H')
  rct_str="%s%s%s%s%s" % (dt[0],str(dt[1]).zfill(2),str(dt[2]).zfill(2),str(dt[3]).zfill(2),str(dt[4]).zfill(2))
  #da_time=datetime.strptime(time_str,'%Y%m%d%H%M') #da cycle time
  rct_time=datetime.strptime(rct_str,'%Y%m%d%H%M') #observation rct from time string
  dhr=(rct_time - da_time).total_seconds()/3600.      #receipt time (relative) equation (in hours)
  return dhr

def compute_latency(t,dt,ob_window,bad_obtime,bad_rctime,bad):
  time_str="%s%s%s%s%s" % (t[0],str(t[1]).zfill(2),str(t[2]).zfill(2),str(t[3]).zfill(2),str(t[4]).zfill(2))
  rct_str="%s%s%s%s%s" % (dt[0],str(dt[1]).zfill(2),str(dt[2]).zfill(2),str(dt[3]).zfill(2),str(dt[4]).zfill(2))
  ob_time=datetime.strptime(time_str,'%Y%m%d%H%M') #observation time from time string
  rct_time=datetime.strptime(rct_str,'%Y%m%d%H%M') #observation rct from time string
  dhr=(rct_time - ob_time).total_seconds()/3600.   #data latency equation (in hours) 
  status=0
  if(ob_time < ob_window[0] or ob_window[1] < ob_time): #ob time is outside window
    #print("\033[Kobtime=%s" % (ob_time))
    bad_obtime+=1
    status=1
  if(rct_cutoff < rct_time): #if receipt time is after the right window/ receipt cutoff
    #print("\033[Krctime=%s" % (rct_time))
    bad_rctime+=1
    status=1
  if(dhr < 0 or 10 < dhr ): #if latency is less than 0 (not possible) or greater than 10 (probably bad data)
    #print("\033[Klatency=%s (%s, %s)" % (dhr*60,ob_time,rct_time))
    bad+=1
    status=1
  return dhr,bad_obtime,bad_rctime,bad,status

def save_dhrs(dhr,sat,air,ins,gps,dhrs_sat,dhrs_air,dhrs_ins,dhrs_gps):
  if(sat and dhr < 100):
    dhrs_sat.append(dhr) #save satellite
  if(air and dhr < 100):
    dhrs_air.append(dhr) #save aircraft
  if(ins and dhr < 100):
    dhrs_ins.append(dhr) #save insitu
  if(gps and dhr < 100):
    dhrs_gps.append(dhr) #save gps 
  return dhrs_sat,dhrs_air,dhrs_ins,dhrs_gps
##############################################################################################################

time=[]      #list for storing dhrs
count=[]     #this is the count for the legend label
names=[]     #this is the name in the legend label
for date in dates:
   colors=[]    #list of colors for the plot
   c=0          #variable for color list
   index=-1
   for path in paths:
      index = index + 1
      dump = dumps[index]  #gfs/gdas/gdas
      dump2= dumps2[index] #gfs/gdas/short
      
      for bufr in bufr_list:
            dhrs_sat=[]      #latency
            dhrs_air=[]      #latency
            dhrs_ins=[]      #latency
            dhrs_gps=[]      #latency
            typ=thisdict[bufr]
            sat=False; air=False; ins=False; gps=False
            if(typ=="sat"): sat=True
            if(typ=="air"): air=True
            if(typ=="ins"): ins=True
            if(typ=="gps"): ins=True
            names.append("%s: %s" % (dump2,bufr))
            name="%s: %s" % (dump2,bufr)    #name
            pdy=date[:8] #cut the date to YYYYMMDD
            cyc=date[8:] #cut the date to CC
            nobs2=0
            
            bufrfile1=path+"%s.%s/%s/%s.t%sz.%s.tm00.bufr_d" % (dump,pdy,cyc,dump,cyc,bufr)

            try:
               bufrin=ncepbufr.open(bufrfile1)
            except:
               print("WARNING no file for %s!!!" %(bufr))
               continue
            bufrfile=bufrfile1

            print("%s (%s): %s" %(name,dump,bufrfile))
            numpy_filename="%s.%s" %(bufr,str(date))


            while bufrin.advance() == 0: #loop over bufr messages
               while bufrin.load_subset() == 0: #loop over subset in bufr message
                  #if(nobs % 10000 == 0):
                   #print("nobs(%s)=%s, nobs(total)=%s, yesRCT=%s, noRCT=%s, bad_rctime=%s, bad_obtime=%s, bad=%s" %\
                   # (bufr,str(nobs2),str(nobs),str(yesRCT),str(noRCT),str(bad_rctime),str(bad_obtime),str(bad)))#, \
                    # end="\r")

                  #read observation time
                  hdr1 = (bufrin.read_subset(hdstr1).squeeze()).filled(0) #parse header string
                  t=[int(x) for x in hdr1[0:5]] #store hdr[1,2,3,4,5] in list "t" YEAR MNTH DAYS HOUR MINU

                  #read receipt time - initial read
                  #hdr2 = (bufrin.read_subset(hdstr2).squeeze()).filled(0) #parse header string
                  hdr2 = (bufrin.read_subset(hdstr2)).filled(0) #parse header string
                  if(len(hdr2[0]) == 0): #means it didn't fill in, read from header
                    try: #sometimes theres a -1 in there that messes things up
                      dt=list((datetime.strptime(str(bufrin.receipt_time),'%Y%m%d%H%M')).timetuple())
                      dt=[int(x) for x in dt[0:5]] #receipt time is in bufr header not in the subsets
                    except:
                      continue #just skip the -1
                    try:
                      obs=len(dt)
                    except:
                      obs=1 #sometimes there is only one level
                  else:
                    obs=len(hdr2[0])             

                  #processing for most data
                  if(obs==1):
                    try: #there are two places the receipt could be. Try this first
                      dt=list((datetime.strptime(str(bufrin.receipt_time),'%Y%m%d%H%M')).timetuple())
                      dt=[int(x) for x in dt[0:5]] #receipt time is in bufr header not in the subsets
                      nhed+=1
                    except: #otherwise the receipt times are here
                      dt=[int(x) for x in hdr2[0:5]]
                      nsub+=1
                    #check if receipt is valid
                    status=0
                    dt,yesRCT,noRCT,nobs,nobs2,status=check_receipt(dt,yesRCT,noRCT,nobs,nobs2)
                    if(status>0):
                      statgt0_count+=1
                      continue
                    #compute latency
                    #dhr,bad_obtime,bad_rctime,bad,status=compute_latency(t,dt,ob_window,bad_obtime,bad_rctime,bad)
                    #compute relative receipt time
                    dhr=compute_receipt(date,dt)
                    if(status>0):
                      statgt0_count+=1
                      continue
                    #save dhr to dhrs
                    dhrs_sat,dhrs_air,dhrs_ins,dhrs_gps=save_dhrs(dhr,sat,air,ins,gps,dhrs_sat,dhrs_air,dhrs_ins,dhrs_gps)

                  #processing for adpupa having multiple levels per subset
                  if(obs>1):
                    for o in range(obs):
                      try:
                        dt=[int(x) for x in hdr2[0:5,o]]
                        nsub+=1
                      except:
                        dt=list((datetime.strptime(str(bufrin.receipt_time),'%Y%m%d%H%M')).timetuple())
                        dt=[int(x) for x in dt[0:5]] #receipt time is in bufr header not in the subsets 
                        nhed+=1
                      status=0
                      #check if receipt is valid
                      dt,yesRCT,noRCT,nobs,nobs2,status=check_receipt(dt,yesRCT,noRCT,nobs,nobs2)
                      if(status>0):
                        statgt0_count+=1
                        continue
                      #compute latency
                      #dhr,bad_obtime,bad_rctime,bad,status=compute_latency(t,dt,ob_window,bad_obtime,bad_rctime,bad)
                      #compute relative receipt time
                      dhr=compute_receipt(date,dt)
                      if(status>0):
                        statgt0_count+=1
                        continue
                      #save dhr to dhrs
                      dhrs_sat,dhrs_air,dhrs_ins,dhrs_gps=save_dhrs(dhr,sat,air,ins,gps,dhrs_sat,dhrs_air,dhrs_ins,dhrs_gps)

            if(sat):
              np.save(numpy_filename, dhrs_sat)
            if(air):
              np.save(numpy_filename, dhrs_air)
            if(ins):
              np.save(numpy_filename, dhrs_ins)
            if(gps):
              np.save(numpy_filename, dhrs_gps)
              
print("\n")
print(nhed,nsub)
print(len(dhrs_ins))
print(statgt0_count)

