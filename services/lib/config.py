"""
$Author: magnun $
$Id: config.py,v 1.10 2002/09/19 22:21:05 magnun Exp $
$Source: /usr/local/cvs/navbak/navme/services/lib/config.py,v $

Implements the singleton pattern ensuring only one
instance created.
"""
import os, re

CONFIGFILEPATH=['/usr/local/navme/etc/conf/','.']

class Conf(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self)
        self._configfile=None
        for path in CONFIGFILEPATH:
            file=os.path.join(os.path.abspath(path),self._file)
            try:
                self._configfile=open(file, "r")
                break
            except IOError:
                pass

        if self._configfile is None:
            print "Failed to open %s" % self._file
            print str(info)
            os.sys.exit(0)
        self._regexp=re.compile(r"^([^#=]+)\s*=\s*([^#\n]+)",re.M)
        self.parsefile()

    def parsefile(self):
        for (key, value) in self._regexp.findall(self._configfile.read()):
            if self.validoptions:
                if key.strip() in self.validoptions:
                    self[key.strip()]=value.strip()
            else:
                self[key.strip()]=value.strip()

def dbconf(*args, **kwargs):
    if _dbconf._instance is None:
        _dbconf._instance=_dbconf(*args,**kwargs)
    return _dbconf._instance

class _dbconf(Conf):
    _instance=None
    def __init__(self, *args, **kwargs):
        self._file=kwargs.get('configfile','db.conf')
        # Valid configoptions must be specified in this list
        self.validoptions=["dbhost", "dbport", "db_nav", "userpw_manage"]
        Conf.__init__(self, *args, **kwargs)

class _serviceconf(Conf):
    _instance=None
    def __init__(self, *args, **kwargs):
        self._file=kwargs.get('configfile','servicemon.conf')
        self.validoptions=[]
        Conf.__init__(self, *args, **kwargs)


def serviceconf(*args, **kwargs):
    if _serviceconf._instance is None:
        _serviceconf._instance=_serviceconf(*args,**kwargs)
    return _serviceconf._instance

class _pingconf(Conf):
    _instance=None
    def __init__(self, *args, **kwargs):
        self._file=kwargs.get('configfile','pinger.conf')
        self.validoptions=[]
        Conf.__init__(self, *args, **kwargs)


def pingconf(*args, **kwargs):
    if _pingconf._instance is None:
        _pingconf._instance=_pingconf(*args,**kwargs)
    return _pingconf._instance



