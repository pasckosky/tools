#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, re, glob, math
import subprocess
from subprocess import *
import codecs

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

def show_help():
    def p(x):
        print >> sys.stderr, x
    p("Usage %s [options] <dir and file list>"%sys.argv[0])
    p("""Options:
    --help: Show this help
    -h:     Show this help
    -a:     All files in current working directory
    -n:     Sort by name
    -s:     Sort by size
    -p:     Hide perc column
    -r:     reverse list (even if not sorted)
    -w:     dynamic bar length (expands to half terminal)
    -z:     poor's man graphics
    """)
    sys.exit(1)

def unknown(cmd):
    print >> sys.stderr, "Unknown option '%s'"%cmd
    show_help()

flist = []
options = {'sort_name': False,
           'sort_size': False,
           'reverse': False,
           'all': False,
           'perc': True,
           'wide': False,
           'utf8': True,
           }
def setopt(key,value):
    options[key] = value

option_map = {
    'h': show_help,
    's': lambda x: setopt('sort_size', True),
    'n': lambda x: setopt('sort_name', True),
    'r': lambda x: setopt('reverse', True),
    'a': lambda x: setopt('all', True),
    'p': lambda x: setopt('perc', False),
    'w': lambda x: setopt('wide', True),
    'z': lambda x: setopt('utf8', False),
    }
    

keyok = True
for x in sys.argv[1:]:
    if x == "-":
        # lonely dash means stdin
        flist.append(None)
    else:
        opt = False
        if keyok:
            if x=='--':
                keyok = False
            elif x[0:1] == '--':
                # long options
                if x == "--help":
                    show_help()
                unknown(x)
                opt = True
            elif x[0] == '-':
                # short options
                for o in x[1:]:
                    handler = option_map.get(o, unknown)
                    handler(o)
                opt = True
        if not opt:
            flist.append(x)

def flatten(l):
    return [ item for sublist in l for item in sublist ]

if len(flist)==0:
    flist = ['.']

if options['all']:
    flist = [ [os.path.join(f, '*'), os.path.join(f, '.*')] for f in flist ]
    flist = flatten(flist)
    flist = [ glob.glob(pattern) for pattern in flist ]
    flist = flatten(flist)

def get_stdin():
    y = sys.stdin.read()
    return [ x.strip() for x in y.split("\n") if len(x.strip())!=0]

if None in flist:
    print >> sys.stderr, "Getting list from stdin"
    stdin = get_stdin()
    none_done = False
    flist1 = []
    for y in flist:
        if y is None:
            if not none_done:
                flist1 += stdin
                none_done = True
        else:
            flist1.append(y)
    flist = flist1

cmd = [ "du", "-sk" ] + flist

try:
    out = check_output(cmd)
except CalledProcessError,e:
    print >> sys.stderr, "Some errors found while executing command. Output can be inaccurate"
    out = e.output

dirs = [ x.split("\t") for x in out.split("\n") if len(x)>0 ]

total_k = sum([ int(a) for a,b in dirs ])
max_k = max([ int(a) for a,b in dirs ])

def sorting(by_name, by_size, data):
    def cmp_name(a,b):
        if a[1]<b[1]:
            return -1
        elif a[1]==b[1]:
            return 0
        else:
            return 1

    def cmp_size(a,b):
        ka = int(a[0])
        kb = int(b[0])
        return ka - kb

    def cmp_combined(a,b):
        r = cmp_size(a,b)
        if r == 0:
            r = cmp_name(a,b)
        return r

    if by_name and by_size:
        return sorted(data,cmp_combined)
    elif by_name:
        return sorted(data,cmp_name)
    elif by_size:
        return sorted(data,cmp_size)
    else:
        return data

def identity(a):
    return a
    
rev = { True: reversed, False: identity}[options['reverse']]
data = [ (int(k),n, (float(k)*100./total_k), (float(k)*100./max_k)) for k,n in rev(sorting(options['sort_name'],options['sort_size'],dirs)) ]

def hr(k):
    if k<1024:
        return "%d kB"%k
    k/=1024.
    if k<1024:
        return "%.1f MB"%k
    k/=1024.
    if k<1024:
        return "%.1f GB"%k
    k/=1024.
    return "%.1f TB"%k

def ralign(t,nch):
    d = nch - len(t)
    if d > 0:
        t = " "*d + t
    return t
    
def bar(p, nmax, beauty):
    # s = u"░▏▎▍▌▋▊▉▉"
    if beauty:
        s = u"·▏▎▍▌▋▊▉▉"
    else:
        s = u".{[(|)]}*"
    n = p/100.*nmax
    ni = int(math.floor(n))
    nf = int(math.floor((n - ni)*len(s)))
    if ni == nmax:
        return s[-1]*nmax
    elif beauty:  
        return u"%s%s%s"%(s[-1]*ni,s[nf],s[0]*(nmax-ni-1))
    else:
        return "%s%s%s"%(s[-1]*ni,s[nf],s[0]*(nmax-ni-1))

fmt = u"%(size)s %(perc)s %(bar)s %(name)s" if options['perc'] else u"%(size)s %(bar)s %(name)s"

lenbar = 20
if options['wide']:
    rows, columns = [ int(x) for x in os.popen('stty size', 'r').read().split() ]
    w0 = 19 if options['perc'] else 11
    # Half of the screen for filenames    
    lenbar = (columns / 2) - w0
    if lenbar<10:
        # provide a minimum
        lenbar = 10

if options['utf8']:
    beauty = True if sys.stdout.encoding == "UTF-8" else False
    if not beauty:
        utf8 = codecs.getwriter('utf8')
        sys.stdout = utf8(sys.stdout)
        beauty=True
else:
    beauty=False
   
        
for k,n,p,b in data:
    print fmt%{'size':ralign(hr(k),10),
               'perc':ralign("%.2f%%"%p, 7),
               'bar':bar(b,lenbar,beauty),
               'name':n.decode('utf-8')
               }
print fmt%{'size':ralign(hr(total_k),10),
           'perc':ralign("100%", 7),
           'bar':ralign("",lenbar),
           'name': "Total"}
