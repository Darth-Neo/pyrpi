#!/usr/bin/env
# __author__ = u"james.morris"
import os
import sys


def getColor(x):
    r = 0
    g = 0
    b = 0

    r = x & (1 << 0)
    g = (x & (1 << 1)) >> 1
    b = (x & (1 << 2)) >> 2

    print(u"%d - %d - %d - %d" % (x, r, g, b))

    return r, g, b

if __name__ == u"__main__":
    cwd = os.getcwd()

    colorset = list()

    for x in range(0, 8):
        r, g, b = getColor(x)
        color = (r, g, b)
