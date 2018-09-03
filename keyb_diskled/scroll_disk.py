#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os
import sys
import time
import subprocess
from subprocess import *


last_v = None

# The code to demonize has been stolen here:
# http://code.activestate.com/recipes/66012-fork-a-daemon-process-on-unix/    

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

def main():
    last = None
    while True:
        curr = get_rw_op(f)
        led(curr!=last)
        if last!=curr:
            last = curr
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    os.chdir("/")
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent, print eventual PID before
            print "Daemon PID %d" % pid
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    main()
