#!/bin/env python

import subprocess, os
import psutil, sys, time
import functools, operator, collections

class Proc(object):
    def __init__(self, p):
        self.p=p
        self.pid=p.pid
        self.data={}
        self.prev_rchar=0.0
        self.prev_wchar=0.0

    def update(self):
        try:
            pio=self.p.io_counters()
            mem=self.p.memory_info()

            delta_rchar=pio.read_chars-self.prev_rchar
            delta_wchar=pio.write_chars-self.prev_wchar

            self.prev_rchar=pio.read_chars
            self.prev_wchar=pio.write_chars

            self.data = {"rss": mem.rss, "vms":mem.vms, "rchar":delta_rchar, "wchar":delta_wchar, "cpu":self.p.cpu_percent(interval=0.01)}
            return self
        except:
            return None

    def __str__(self):
        return f'{self.pid}: {self.data}'

def sumDicts(dicts):
    return dict(functools.reduce(operator.add,map(collections.Counter, dicts)))

def getProcs(toppid):
    try:
        p=psutil.Process(int(toppid))
    except psutil.NoSuchProcess:
        return []

    procs= list(map(Proc, [p]+p.children(recursive=True)))
    return procs

def updateAll(ps):
    return [p for p in ps if p.update()]

cols=["timestamp", "pid", "cpu", "rss", "vms", "rchar", "wchar"]

def dump(fp, ps):
    now=time.time()-begintime
    if ps:
        for p in ps:
            d={"timestamp":now, "pid": p.pid}
            d.update(p.data)
            fp.write("\t".join([str(d[k]) for k in cols])+'\n')
        
        #d={"timestamp":now, "pid": 0}
        #d.update(sumDicts([p.data for p in ps]))
        #fp.write("\t".join([str(d[k]) for k in cols])+'\n')
        fp.flush()

if __name__=='__main__':
    interval=int(os.environ.get('MONITOR_INTERVAL', 5))
    outputFile=os.environ.get('MONITOR_OUTPUT', 'monitor.out')
    of=open(outputFile, 'w')
    of.write("\t".join(cols)+'\n')

    begintime=time.time()
    P=subprocess.Popen(sys.argv[1:])
    pid=P.pid
    ret=None
    while ret == None:
        ps=getProcs(pid)
        ps=updateAll(ps)
        dump(of, ps)
        try:
            ret=P.wait(timeout=interval)
        except subprocess.TimeoutExpired:
            pass
    # finish up
    exit(ret)

