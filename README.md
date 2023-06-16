# Monitor


## To install
Create a conda env that contains python3, psutil, pandas, and matplotlib

Optionally jupyter if you want to run the display code in jupyter

## To run

python3 monitor.py prog arg1 arg2 arg3

By default, the process is polled every 5 seconds and output is in monitor.out

MONITOR_INTERVAL=30 MONITOR_OUTPUT=my.out python3 monitor.py prog arg1 arg2 arg3

