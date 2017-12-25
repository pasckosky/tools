# -*- coding: utf-8 -*-

from ansi import p_ok, p_err, p_info
import sys
import codecs

def is_verbose(opt):
    return opt.get("verbose",False)

def request_http(opt):
    verbose = is_verbose(opt)
    
    try:
        #raise Exception, "test"
        import requests
        advanced = True
    except:
        import urllib2
        advanced = False

    def request_page_advanced(url):
        if verbose:
            print "Looking for %s ..."%url
        r = requests.get(url)
        if r.status_code == 200:
            page = r.text
            r.close()
            return page
        else:
            p_err("Error %d on HTTP request"%r.status_code, opt=opt)
            r.close()
            return ""

    def request_page_old(url):
        if verbose:
            print "Looking for %s ... (with urlib2)"%url
        f = urllib2.urlopen(url)
        status_code = 200 #f.getcode()
        try:
            page = f.read()
        except:
            p_err("Error on HTTP request", opt=opt)
            page = ""    
        f.close()
        return page
        
    return request_page_advanced if advanced else request_page_old

def check_version(ref_version, opt):
    fn_get = request_http(opt)
    lastest_url = "https://raw.githubusercontent.com/pasckosky/tools/master/dug/dist/lastest"
    lastest_version = fn_get(lastest_url).strip()
    p_ok ("Lastes version is %s"%lastest_version, opt=opt)
    p_info ("You have version %s"%ref_version, opt=opt)
    sys.exit(0)
    
def download_last(ref_version, dest_fname, update, opt):
    fn_get = request_http(opt)
    lastest_url = "https://raw.githubusercontent.com/pasckosky/tools/master/dug/dist/lastest"
    lastest_version = fn_get(lastest_url).strip()
    
    if update and lastest_version == ref_version:
        p_ok("You already have the last version", opt=opt)
        sys.exit(0)
    if update:
        p_info("You have version %s, downloading version %s"%(ref_version,lastest_version), opt=opt)
    
    if lastest_version == "":
        p_err("Errors while checking lastest version", opt=opt)
        sys.exit(1)
    ver_url = "https://raw.githubusercontent.com/pasckosky/tools/master/dug/dist/dug_%s.py"%lastest_version
    script_file = fn_get(ver_url)
    if script_file == "":
        p_err("Errors while getting lastest version", opt=opt)
        sys.exit(1)
        
    fout = open(dest_fname,"w")
    utf8 = codecs.getwriter('utf8')
    utf8(fout).write(script_file)
    fout.close()
    p_ok("File version %s has been saved as %s"%(lastest_version,dest_fname), opt=opt)
    if not update:
        p_info("Move it wherever you please", opt=opt)
    sys.exit(0)
