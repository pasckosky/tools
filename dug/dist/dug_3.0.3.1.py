#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import os
import re
import glob
import math
import subprocess
from subprocess import *
import codecs
from functools import cmp_to_key

__version__ = "3.0.3.1"

# ANSI COLOR SECTION


def rgb(r, g, b, bgnd=False):
    assert(0 <= r <= 5)
    assert(0 <= g <= 5)
    assert(0 <= b <= 5)
    code = 48 if bgnd else 38
    return "\x1b[%d;5;%dm" % (code, 16+b+6*g+36*r)


def gray(l, bgnd=False):
    assert(0 <= l <= 23)
    code = 48 if bgnd else 38
    return "\x1b[%d;5;%dm" % (code, 232+l)


def reset_color():
    return "\x1b[0m"


def std(l, bgnd=False):
    assert(0 <= l <= 15)
    code = 48 if bgnd else 38
    return "\x1b[%d;5;%dm" % (code, l)


ASCII_ONLY = 1
T16COLORS = 2
T256COLORS = 3


def typeofterm():
    term = os.environ.get("TERM", "")
    if term.endswith("256color"):
        return T256COLORS
    elif term != "":
        return T16COLORS
    else:
        return ASCII_ONLY


# END of ANSI


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


def show_help(x):
    def p(x):
        print(x, file=sys.stderr)
    p("DUG version %s" % __version__)
    p("Usage %s [options] <dir and file list>" % sys.argv[0])
    p("""Options:
    --help: Show this help
    -h:     Show this help
    -a:     All files in current working directory
    -n:     Sort by name
    -N:     Sort by name (natural)
    -D:     Sort by file/dir modification date
    -s:     Sort by size
    -p:     Hide perc column
    -r:     reverse list (even if not sorted)
    -w:     dynamic bar length (expands to half terminal)
    -z:     poor's man graphics
    -c:     colorize output
    -C:     vertical colorization
    """)
    p("")
    p("""Special options:
    --get_new <dest_fname>:    Get lastest version of dug and save as dest_fname (full path)
    --check:                   Check for updates
    --update:                  Update if necessary
    """)
    sys.exit(1)


def unknown(cmd):
    print("Unknown option '%s'" % cmd, file=sys.stderr)
    show_help(None)


flist = []
options = {'sort_name': False,
           'sort_name_natural': False,
           'sort_size': False,
           'sort_date': False,
           'reverse': False,
           'all': False,
           'perc': True,
           'wide': False,
           'utf8': True,
           'color': False,
           'colorvert': False,
           'ncolors': typeofterm(),
           }


def setopt(key, value):
    options[key] = value


option_map = {
    'h': show_help,
    's': lambda x: setopt('sort_size', True),
    'n': lambda x: setopt('sort_name', True),
    'N': lambda x: setopt('sort_name_natural', True),
    'D': lambda x: setopt('sort_date', True),
    'r': lambda x: setopt('reverse', True),
    'a': lambda x: setopt('all', True),
    'p': lambda x: setopt('perc', False),
    'w': lambda x: setopt('wide', True),
    'z': lambda x: setopt('utf8', False),
    'c': lambda x: setopt('color', True),
    'C': lambda x: (setopt('colorvert', True), setopt('color', True)),
}


def p_ok(text, on_err=False):
    fout = sys.stderr if on_err else sys.stdout
    if not options['color'] or options["ncolors"] == ASCII_ONLY:
        print(text, file=fout)
    else:
        print("%s%s%s" % (std(2), text, reset_color()), file=fout)


def p_info(text, on_err=False):
    fout = sys.stderr if on_err else sys.stdout
    if not options['color'] or options["ncolors"] == ASCII_ONLY:
        print(text, file=fout)
    else:
        print("%s%s%s" % (std(3), text, reset_color()), file=fout)


def p_err(text):
    if not options['color'] or options["ncolors"] == ASCII_ONLY:
        print(text, file=sys.stderr)
    else:
        print("%s%s%s" % (std(1), text, reset_color()), file=sys.stderr)


def p_out(text, on_err=False):
    fout = sys.stderr if on_err else sys.stdout
    print(text, file=fout)


def request_http():
    try:
        #raise Exception, "test"
        import requests
        advanced = True
    except:
        import urllib.request
        import urllib.error
        import urllib.parse
        advanced = False

    def request_page_advanced(url):
        r = requests.get(url)
        if r.status_code == 200:
            page = r.text
            r.close()
            return page
        else:
            p_err("Error %d on HTTP request" % r.status_code)
            r.close()
            return ""

    def request_page_old(url):
        print("Old request of %s" % url)
        f = urllib.request.urlopen(url)
        status_code = 200  # f.getcode()
        try:
            page = f.read()
        except:
            p_err("Error on HTTP request")
            page = ""
        f.close()
        return page

    return request_page_advanced if advanced else request_page_old


def check_version(ref_version):
    fn_get = request_http()
    lastest_url = "https://raw.githubusercontent.com/pasckosky/tools/master/dug/dist/lastest"
    lastest_version = fn_get(lastest_url).strip()
    p_ok("Lastes version is %s" % lastest_version)
    p_info("You have version %s" % ref_version)
    sys.exit(0)


def download_last(ref_version, dest_fname, update):
    fn_get = request_http()
    lastest_url = "https://raw.githubusercontent.com/pasckosky/tools/master/dug/dist/lastest"
    lastest_version = fn_get(lastest_url).strip()

    if update and lastest_version == ref_version:
        p_ok("You already have the last version")
        sys.exit(0)
    if update:
        p_info("You have version %s, downloading version %s" %
               (ref_version, lastest_version))

    if lastest_version == "":
        p_err("Errors while checking lastest version")
        sys.exit(1)
    ver_url = "https://raw.githubusercontent.com/pasckosky/tools/master/dug/dist/dug_%s.py" % lastest_version
    script_file = fn_get(ver_url)
    if script_file == "":
        p_err("Errors while getting lastest version")
        sys.exit(1)

    fout = open(dest_fname, "wb")
    #utf8 = codecs.getwriter('utf8')
    # utf8(fout).write(script_file.decode("utf-8"))
    fout.write(script_file)
    fout.close()
    p_ok("File version %s has been saved as %s" %
         (lastest_version, dest_fname))
    if not update:
        p_info("Move it wherever you please")
    sys.exit(0)


keyok = True
download = False
for x in sys.argv[1:]:
    if download:
        dest_fname = x
        download_last(__version__, dest_fname, False)
    elif x == "-":
        # lonely dash means stdin
        flist.append(None)
    else:
        opt = False
        if keyok:
            if x == '--':
                keyok = False
            elif x[:2] == '--':
                # long options
                if x == "--help":
                    show_help(None)
                elif x == "--check":
                    check_version(__version__)
                elif x == "--get_new":
                    download = True
                    continue
                elif x == "--update":
                    me = sys.argv[0]
                    download_last(__version__, me, True)
                else:
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
if download:
    download_last(__version__, "/tmp/dug.py", False)


def flatten(l):
    return [item for sublist in l for item in sublist]


if len(flist) == 0:
    flist = ['.']

if options['all']:
    flist = [[os.path.join(f, '*'), os.path.join(f, '.*')] for f in flist]
    flist = flatten(flist)
    flist = [glob.glob(pattern) for pattern in flist]
    flist = flatten(flist)


def get_stdin():
    y = sys.stdin.read()
    return [x.strip() for x in y.split("\n") if len(x.strip()) != 0]


if None in flist:
    p_info("Getting list from stdin", True)
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

cmd = ["du", "-sk"] + flist

try:
    out = check_output(cmd)
except CalledProcessError as e:
    p_err("Some errors found while executing command. Output can be inaccurate")
    out = e.output

dirs = [x.split(b"\t") for x in out.split(b"\n") if len(x) > 0]

total_k = sum([int(a) for a, b in dirs])
max_k = max([int(a) for a, b in dirs])


def undot(s):
    d, f = os.path.dirname(s), os.path.basename(s)
    if f[0] == '.':
        f = f[1:]
    return os.path.join(d, f)


date_kb = {}


def sorting(options, data):

    # function for choosing the right comparer
    def choose_compare(by_name, natural, by_size, by_date):
        def cmp_name(a, b):
            ta = a[1]
            tb = b[1]
            if natural:
                ta = undot(ta)
                tb = undot(tb)
            if ta < tb:
                return -1
            elif ta == tb:
                return 0
            else:
                return 1

        def cmp_size(a, b):
            ka = int(a[0])
            kb = int(b[0])
            return ka - kb

        def cmp_date(a, b):
            global date_kb

            na = a[1]
            nb = b[1]

            da = date_kb.get(na, None)
            db = date_kb.get(nb, None)

            def get_mtime(path):
                s = os.stat(path)
                return s.st_mtime
            if da is None:
                da = get_mtime(na)
                date_kb[na] = da
            if db is None:
                db = get_mtime(nb)
                date_kb[nb] = db

            if da < db:
                return -1
            elif da > db:
                return 1
            else:
                return 0

        if natural:
            by_name = True

        functions = []
        if by_name:
            functions.append(cmp_name)
        if by_size:
            functions.append(cmp_size)
        if by_date:
            functions.append(cmp_date)

        if len(functions) == 0:
            # No sorting
            return None

        # One or more criteria has been chosen
        def cmp_combined(a, b):
            """ sort by applying all selected criteria """
            r = 0
            for f in functions:
                r = f(a, b)
                if r != 0:
                    return r
            return r
        return cmp_combined

    # Choose comparer and apply it, if found
    cmp_func = choose_compare(
        options['sort_name'], options['sort_name_natural'], options['sort_size'], options['sort_date'])
    if cmp_func is None:
        # No sorting
        return data
    # do sorting
    return sorted(data, key=cmp_to_key(cmp_func))


def identity(a):
    return a


rev = {True: reversed, False: identity}[options['reverse']]
if total_k == 0:
    total_k = 1
if max_k == 0:
    max_k = 1
data = [(int(k), n, (float(k)*100./total_k), (float(k)*100./max_k))
        for k, n in rev(sorting(options, dirs))]


def hr(k):
    if k < 1024:
        return "%d kB" % k
    k /= 1024.
    if k < 1024:
        return "%.1f MB" % k
    k /= 1024.
    if k < 1024:
        return "%.1f GB" % k
    k /= 1024.
    return "%.1f TB" % k


def ralign(t, nch):
    d = nch - len(t)
    if d > 0:
        t = " "*d + t
    return t


def calc_perc(p, b, nmax):
    t = ralign("%.2f%%" % p, 7)
    if not options['color'] or options["ncolors"] == ASCII_ONLY or not options['perc']:
        return t

    n = b/100.*nmax
    if options['ncolors'] == T16COLORS:
        if b <= 33.33:
            col = std(2)
        elif b <= 66.66:
            col = std(3)
        else:
            col = std(1)
    else:
        pc = round(b/100.*5)
        col = rgb(pc, 5-pc, 0)

    return u"%s%s%s" % (col, t, reset_color())


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
        s = s[-1]*nmax
    elif beauty:
        s = u"%s%s%s" % (s[-1]*ni, s[nf], s[0]*(nmax-ni-1))
    else:
        s = "%s%s%s" % (s[-1]*ni, s[nf], s[0]*(nmax-ni-1))

    if not options['color'] or options["ncolors"] == ASCII_ONLY:
        return s
    elif options['colorvert']:
        if options["ncolors"] == T16COLORS:
            l1 = nmax/3
            data = {
                "g": s[:l1],
                "y": s[l1:-l1],
                "r": s[-l1:],
                "cg": std(2),
                "cy": std(3),
                "cr": std(1),
                "end": reset_color()
            }
            return u"%(cg)s%(g)s%(cy)s%(y)s%(cr)s%(r)s%(end)s" % data
        else:
            ns = int(round(nmax/6.))
            sect = u"".join(
                [u"".join((rgb(x, 5-x, 0), s[x*ns:(x+1)*ns])) for x in range(6)])
            sect += s[6*ns:]
            return sect+reset_color()
    elif options["ncolors"] == T16COLORS:
        if p <= 33.33:
            col = 2  # green
        elif p <= 66.66:
            col = 3  # yellow
        else:
            col = 1  # red
        return u"%s%s%s" % (std(col), s, reset_color())
    else:
        pc = round(p/100.*5)
        return u"%s%s%s" % (rgb(pc, 5-pc, 0), s, reset_color())


fmt = u"%(size)s %(perc)s %(bar)s %(name)s" if options['perc'] else u"%(size)s %(bar)s %(name)s"

lenbar = 20
if options['wide']:
    rows, columns = [int(x) for x in os.popen('stty size', 'r').read().split()]
    w0 = 19 if options['perc'] else 11
    # Half of the screen for filenames
    lenbar = (columns / 2) - w0
    if lenbar < 10:
        # provide a minimum
        lenbar = 10
lenbar = int(lenbar)


def is3_8(v):
    if v.major == 3:  # and v.minor >= 8:
        return True
    elif v.major > 3:
        return True
    return False


if options['utf8']:
    beauty = True if sys.stdout.encoding == "UTF-8" else False
    if not beauty:
        utf8 = codecs.getwriter('utf8')
        if sys.version_info.major >= 3:
            # for Python3 we want stdout as binary stream
            # in order to use stream rewriter
            sys.stdout = os.fdopen(sys.stdout.fileno(), "wb", closefd=False)
        sys.stdout = utf8(sys.stdout)
        beauty = True
else:
    beauty = False


for k, n, p, b in data:
    p_out(fmt % {'size': ralign(hr(k), 10),
                 'perc': calc_perc(p, b, lenbar),
                 'bar': bar(b, lenbar, beauty),
                 'name': n.decode('utf-8')
                 })
p_out(fmt % {'size': ralign(hr(total_k), 10),
             'perc': ralign("100%", 7),
             'bar': ralign("", lenbar),
             'name': "Total"})
