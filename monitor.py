#!/bin/env python

import subprocess, os
import psutil, sys, time
import functools, operator, collections

procMap={}

class Proc(object):

    procTree={}
    toppid=None

    def __init__(self, p):
        self.p=p
        self.pid=p.pid
        self.data={}
        self.prev_rchar=0.0
        self.prev_wchar=0.0
        self.children=[]
        self.p.cpu_percent() # prime the pump
        self.cmdline=" ".join(p.cmdline())

    @classmethod
    def add(cls, p):
        P=Proc(p)
        cls.procTree[p.pid]=P
        if p.pid != cls.toppid:
            cls.procTree[p.ppid()].children.append(p.pid)

    @classmethod
    def dumpTree(cls, pid, level=0):
        P=cls.procTree[pid]
        print ("%s%s: %s" % ("\t"*level, pid, P.cmdline))
        for pid in P.children:
            cls.dumpTree(pid, level+1)
        
    def update(self, now):
        try:
            pio=self.p.io_counters()
            mem=self.p.memory_info()

            delta_rchar=pio.read_chars-self.prev_rchar
            delta_wchar=pio.write_chars-self.prev_wchar

            self.prev_rchar=pio.read_chars
            self.prev_wchar=pio.write_chars

            self.data = {"timestamp": now, "pid":self.pid, "rss": mem.rss, "vms":mem.vms, "rchar":delta_rchar, "wchar":delta_wchar, "cpu":self.p.cpu_percent()}
            return self.data
        except:
            return None

    def __str__(self):
        return "%d: %s" % (self.pid, str(self.data))

def sumDicts(dicts):
    return dict(functools.reduce(operator.add,map(collections.Counter, dicts)))

cols=["timestamp", "pid", "cpu", "rss", "vms", "rchar", "wchar"]

def updateProcs(fp):
    try:
        p=psutil.Process(int(Proc.toppid))
    except psutil.NoSuchProcess:
        return

    procs=[p]+p.children(recursive=True)
    for p in procs:
        if p.pid not in Proc.procTree:
            Proc.add(p)
 
    now=(time.time()-begintime)
    for pid, P in Proc.procTree.items():
        d=P.update(now)
        if d:
            fp.write("\t".join([str(d[k]) for k in cols])+'\n')
    fp.flush()

if __name__=='__main__':
    interval=int(os.environ.get('MONITOR_INTERVAL', 5))
    outputFile=os.environ.get('MONITOR_OUTPUT', 'monitor.out')
    of=open(outputFile, 'w')
    of.write("\t".join(cols)+'\n')

    begintime=time.time()
    try:
        P=subprocess.Popen(" ".join(sys.argv[1:]), shell=True)

        Proc.toppid=P.pid
        ret=None
        while ret == None:
            updateProcs(of)
            try:
                ret=P.wait(timeout=interval)
                print("job ended ret %d" % ret)
            except subprocess.TimeoutExpired:
                pass
    finally:
        # finish up
        Proc.dumpTree(Proc.toppid)
        exit(ret)

