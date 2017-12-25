# -*- coding: utf-8 -*-

import os,sys

# ANSI COLOR SECTION

def rgb(r,g,b, bgnd=False):
    assert( 0 <= r <=5)
    assert( 0 <= g <=5)
    assert( 0 <= b <=5)
    code = 48 if bgnd else 38
    return "\x1b[%d;5;%dm"%(code,16+b+6*g+36*r)

def gray(l, bgnd=False):
    assert( 0 <= l <= 23)
    code = 48 if bgnd else 38
    return "\x1b[%d;5;%dm"%(code,232+l)

def reset_color():
    return "\x1b[0m"

def std(l, bgnd=False):
    assert(0<=l<=15)
    code = 48 if bgnd else 38
    return "\x1b[%d;5;%dm"%(code,l)

ASCII_ONLY = 1
T16COLORS = 2
T256COLORS = 3

def typeofterm():
    term = os.environ.get("TERM","")
    if term.endswith("256color"):
        return T256COLORS
    elif term!="":
        return T16COLORS
    else:
        return ASCII_ONLY

curr_mode = typeofterm()

def is_color(opt):
    return opt.get("color", False)

def p_ok(text, on_err=False, opt={}):
    fout = sys.stderr if on_err else sys.stdout
    if not is_color(opt) or curr_mode == ASCII_ONLY:
        print >>fout, text
    else:
        print >>fout, "%s%s%s"%(std(2),text,reset_color())

def p_info(text, on_err=False, opt={}):
    fout = sys.stderr if on_err else sys.stdout
    if not is_color(opt) or curr_mode == ASCII_ONLY:
        print >>fout, text
    else:
        print >>fout, "%s%s%s"%(std(3),text,reset_color())

def p_err(text, opt={}):
    if not is_color(opt) or curr_mode == ASCII_ONLY:
        print >>sys.stderr, text
    else:
        print >>sys.stderr, "%s%s%s"%(std(1),text,reset_color())

def p_out(text, on_err=False):
    fout = sys.stderr if on_err else sys.stdout
    print >>fout, text

#END of ANSI
