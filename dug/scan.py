# -*- coding: utf-8 -*-

import sys, os
import time, glob
from stat import S_ISDIR

import pprint

def getinfo(path):
    """ 
    isDir, path, inode, size, disk_usage
    Sizes in bytes
    """
    st = os.lstat(path)
    return (S_ISDIR(st.st_mode),path,st.st_ino,st.st_size,st.st_blocks*512)
    
def __scan(verbose, hidden, path):
        
    def walk(base):
        p_hidden = os.path.join(base, ".*")
        p_normal = os.path.join(base, "*")

        def subgen(p):
            for f in glob.glob(p):
                i = getinfo(f)
                yield i
                if i[0]:
                    for x in walk(f):
                        yield x
        
        if hidden:
            for x in subgen(p_hidden):
                yield x
        for x in subgen(p_normal):
            yield x

    i = getinfo(path)
    yield i
    if i[0]:
        for x in walk(path):
            yield x
    
def scan(options, *path):
    """
    Returns a list of tuples (size kb, path) of files and dirs
    that forfills the path requests and options

    files that shares the same inodes (hard-link) are counted only once
    """
    ret = set()
    verbose = options["verbose"]
    get_all = options["all"]

    if len(path) == 0:
        path="."
    
    for p in path:
        ret.update(set(__scan(verbose, get_all, p)))


    if verbose:
        pprint.pprint(ret)
    return []
