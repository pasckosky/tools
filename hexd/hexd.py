#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

def sanitize(r):
    return "".join( x if 32<=ord(x)<=126 else "." for x in r )

def vert_select(origin, rng):
    if rng == []:
        return origin

    nmax = len(origin)
    elt = set()
    for x in rng:
        l = len(x)
        if l == 1:
            elt.add(x[0])
        else:
            c0, c1 = x
            if c0 is None and c1 is None:
                return origin
            elif c0 is None:
                elt = elt.union(set(range(0,c1)))
            elif c1 is None:
                elt = elt.union(set(range(c0,nmax)))
            else:
                elt = elt.union(set(range(c0,c1)))

    return [ x for j,x in enumerate(origin) if j in elt]

def parse_range(cmd, hexv):
    base = 16 if hexv else 10
    def single(e):
        m = [ None if x == "" else int(x, base) for x in e.split("-") ]
        if len(m)==1:
            return (m[0],m[0]+1)
        elif len(m)==2:
            return (min(m),max(m)+1)
        else:
            print "Errore nel formato dei range verticali"
            exit(1)
    
    return [ single(x) for x in cmd.split(",") ]

def hexdump(f,o):
    w = o["width"]
    rng = o['range_vert']
    titles = vert_select([ "%02x"%x for x in range(w)],rng)
    if (o["hex"] or not o["asc"]) and o["headers"]:
        print " "*9+" ".join(titles)
        print "-"*(len(titles)*3+9)
    base = 0
    while True:
        r = f.read(w)
        if r == "":
            break
        l = len(r)
        dumped = ["%02x"%ord(x) for x in r]
        if l<w:
            dumped += ["  "]*(w-l)
        dumped = vert_select(dumped, rng)
        sanitized = ""
        if o['asc']:
            sanitized = sanitize(r)
            if l<w:
                sanitized += " "*(w-l)
            sanitized = "".join(vert_select(sanitized, rng))

        s = []
        if (o["hex"] or not o["asc"]) and o["headers"]:
            s.append("%08x "%base)
        if o["hex"] or not o["asc"]:
            s.append(" ".join(dumped))
        if o["hex"] and o["asc"]:
            s.append(" | ")
        if o["asc"]:
            s.append(sanitized)

        print "".join(s)
        base += l
        
def debug(o,l):
    r = vert_select(o,l)
    print "test on %s with %s: res %s"%(o,str(l),r)

def test():
    a = "0123456789"*3
    debug(a,[])
    debug(a,[[1]])
    debug(a,[[1],[2],[5],[4]])
    debug(a,[[1,3],[2],[5],[4]])
    debug(a,[[None,3],[8],[5],[10]])
    debug(a,[[12,None],[8],[5],[10]])

        
def main(args):
    def pop_or_exit(args):
        if len(args)==0:
            print "Errore"
            exit(1)
        return args.pop()
    
    options = { "width": 16,
                "asc": True,
                "hex": True,
                "headers": True,
                "range_vert": [],
                }
    args.reverse()
    exename = args.pop()
    filename = []
    while len(args)>0:
        o = args.pop()
        if o == "-T":
            test()
            exit(0)
        elif o == "-q":
            options['headers'] = False
        elif o == "+q":
            options['headers'] = True
        elif o == "-w":
            options["width"] = int(pop_or_exit(args))
        elif o == "-a":
            options["asc"] = False
        elif o == "+a":
            options["asc"] = True
        elif o == "-x":
            options["hex"] = False
        elif o == "+x":
            options["hex"] = True
        elif o == "-c" or o == "-C":
            hex = False if o == "-c" else True
            options['range_vert']+=list(parse_range(pop_or_exit(args),hex))
        else:
            filename.append(o)
    if len(filename) == 0:
        print "Specificare almeno un nome di file"
        exit(1)
    try:
        for f in filename:
            hexdump(open(f,"rb"),options)
    except IOError:
        pass
    return 0



    
if __name__ == "__main__":
    exit(main(sys.argv))
        
