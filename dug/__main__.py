#!/usr/bin/env python2
# -*- coding: utf-8; mode: python; -*-

import os, sys
import options
import pprint
import ansi

__version__ = "2.4"

def main(args):
    flist, opt = options.parse(__version__, args)
   
    print "options:"
    pprint.pprint(opt)
    pprint.pprint(flist)
    

if __name__=="__main__":
    sys.exit(main(sys.argv[1:]))
