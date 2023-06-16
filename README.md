# Monitor
This tool runs a program and observes it as it runs, writing records to a file.  Subprocesses are also tracked.  When the program ends, the
output file can be viewed graphically.

## To install
Create a conda env that contains python3, psutil, pandas, and matplotlib.  Optionally jupyter if you want to run the display code in jupyter.

## To run
python3 monitor.py prog arg1 arg2 arg3

By default, the process is polled every 5 seconds and output is in monitor.out.

To choose a different interval and/or output file, use these env vars:
MONITOR_INTERVAL=30 MONITOR_OUTPUT=my.out python3 monitor.py prog arg1 arg2 arg3

## To view
The jupyter notebook shows an initial cut at visualization.  It reads the monitor.out file and shows graphs for IO, Memory, CPU in agregate and by process.
