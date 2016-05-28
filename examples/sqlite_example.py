#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys

if __name__ == u"__main__":
    con = None

    try:
        with lite.connect('test.db') as con:

            cur = con.cursor()
            cur.execute('SELECT SQLITE_VERSION()')

            data = cur.fetchone()

            print "SQLite version: %s" % data

    except lite.Error, e:

        print "Error %s:" % e.args[0]
        sys.exit(1)

    finally:

        if con:
            con.close()


