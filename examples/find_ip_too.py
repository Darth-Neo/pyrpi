#!/usr/bin/env python
__author__ = u"james.morris"
import os
import commands

if __name__ == u"__main__":

    s = commands.getoutput(u"/sbin/ifconfig")
    t = s.split(os.linesep)
    u = t[1]
    v = u.split()
    w = v[1][5:]

    print(u"%s" % w)