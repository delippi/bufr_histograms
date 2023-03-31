Created 6/02/2021
Updated 3/31/2023

This set of scripts is made to inventory bufr observations and create a histogram and a CDF of the data latency.
As there are a lot of observations to processes (~2e8 per 6hrly dump), the process is broken down into three
major steps. The first step, submits 1 job per observation type per cycle. Be careful here not to submit too
many jobs. It is also wise to not try to use too many cycle times. The output of step one are numpy objects that
contain the latency information for each observation type. Step 2 involves reading those numpy files, deciding
what type of observation satellite, aircraft, insitu, or gps and then creating four new numpy files containing
the total counts for each observation type. In step 3, those numpy files created in step 2 are then read
which are then plotted. There is some parts of this final script that can cause out of memory (OOM) errors.
Perhaps there is a better way to coding this? In step 4, the numpy files created in step 1 are used to make the
plots.

FILE DESCRIPTIONS:

src/
    dateutils.py:     Needed for date manipulation
    latency_1.py:      1st step, read each bufr file and output $bufr.$date.npy file to be read by latency2
    latency_2.py:      2nd step  which reads the $bufr.$date.npy then outputs $typ.$date.npy where typ=sat,air,ins,gps
    latency_3.py:      3rd step (only after latency2) which reads the $typ.$date.npy files then plots
    latency_4.py:      4th step (can be run after 1st step) which reads $bufr.$date.npy then plots separately.
    receipt_1.py:      1st step, read each bufr file and output $bufr.$date.npy file to be read by latency2
    receipt_2.py:      2nd step  which reads the $bufr.$date.npy then outputs $typ.$date.npy where typ=sat,air,ins,gps

scripts/
    incdate.sh:       similar to ndate; date manipulation
    bufr.txt:         A text list of bufr file types. Use a "#" to skip individual types. Used by run.ksh.
    config.ksh:       The configuration file. Right now only contains the date1&2 for all three steps.
    run.latency_1.ksh: used to run 1st step python script
    run.latency_2.ksh: used to run 2nd step python script
    run.latency_3.ksh: used to run 3rd step python script
    run.latency_4.ksh: used to run 4rd step python script
    run.receipt_1.ksh: used to run 1st step python script
    run.receipt_2.ksh: used to run 2nd step python script

TO RUN:
0.)   edit config.ksh #this is where you set the dates for the 3 steps.
0.5.) edit bufr.txt   #comment out using "#" the obs types that are not needed.
1.)   ksh run.latency_1.ksh
2.)   ksh run.latency_2.ksh
3.)   ksh run.latency_3.ksh
4.)   ksh run.latency_4.ksh
