#!/usr/bin/env python
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import socket
import sys

from zeroconf import __version__, ServiceInfo, Zeroconf

if __name__ == u'__main__':

    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) > 1:
        assert sys.argv[1:] == [u'--debug']
        logging.getLogger(u'zeroconf').setLevel(logging.DEBUG)

    # Test a few module features, including service registration, service
    # query (for Zoe), and service unregistration.
    print(u"Multicast DNS Service Discovery for Python, version %s" % (__version__,))


    r = Zeroconf()
    print(u"1. Testing registration of a service...")
    desc = {u'version': u'0.10', u'a': u'test value', u'b': u'another value'}
    info = ServiceInfo(u"_http._tcp.local.",
                       u"My Service Name._http._tcp.local.",
                       socket.inet_aton(u"127.0.0.1"), 1234, 0, 0, desc)
    print(u"   Registering service...")
    r.register_service(info)
    print(u"   Registration done.")
    print(u"2. Testing query of service information...")
    print(u"   Getting ZOE service: %s" % (
        r.get_service_info(u"_http._tcp.local.", u"ZOE._http._tcp.local.")))
    print(u"   Query done.")
    print(u"3. Testing query of own service...")
    info = r.get_service_info(u"_http._tcp.local.", u"My Service Name._http._tcp.local.")
    assert info
    print(u"   Getting self: %s" % (info,))
    print(u"   Query done.")
    print(u"4. Testing unregister of service information...")
    r.unregister_service(info)
    print(u"   Unregister done.")
    r.close()