#!/usr/bin/env python

from __future__ import absolute_import, division, print_function, unicode_literals

u""" Example of browsing for a service (in this case, HTTP) """

import logging
import socket
import sys
from time import sleep
import os

from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf


def on_service_state_change(zeroconf, service_type, name, state_change):
    print(u"Service %s of type %s state changed: %s" % (name, service_type, state_change))

    if state_change is ServiceStateChange.Added:
        info = zeroconf.get_service_info(service_type, name)
        if info:
            print(u"  Address: %s:%d" % (socket.inet_ntoa(info.address), info.port))
            print(u"  Weight: %d, priority: %d" % (info.weight, info.priority))
            print(u"  Server: %s" % (info.server,))
            if info.properties:
                print(u"  Properties are:")
                for key, value in info.properties.items():
                    print(u"    %s: %s" % (key, value))
            else:
                print(u"  No properties")
        else:
            print(u"  No info")
        print(u'%s' % os.linesep)

if __name__ == u'__main__':

    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) > 1:
        assert sys.argv[1:] == [u'--debug']
        logging.getLogger(u'zeroconf').setLevel(logging.DEBUG)

    zeroconf = Zeroconf()

    print(u"%sBrowsing services, press Ctrl-C to exit...%s" % (os.linesep, os.linesep))

    browser = ServiceBrowser(zeroconf, u"_http._tcp.local.", handlers=[on_service_state_change])

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.close()