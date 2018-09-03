#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import time
import subprocess
from subprocess import *

last_v = None

def check_output(*popenargs, **kwargs):
    """ Imported function from Python 2.7.x because it is not present in Python 2.6.x """
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = Popen(stdout=PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise CalledProcessError(retcode, cmd, output=output)
    return output

def led(v):
    global last_v
    if v!=last_v:
        check_output(["xset", "led" if v else "-led", "3"])
    last_v = v

def get_rw_op(fl):
    n = [ [ int(y) for y in open(x,"r").read().strip().split() ] for x in fl ]
    return sum([x[0]+x[4] for x in n ])

f = [ "/sys/block/sda/stat", "/sys/block/sdb/stat" ]

last = None
while True:
    curr = get_rw_op(f)
    led(curr!=last)
    if last!=curr:
        last = curr
    time.sleep(0.1)
        
    

