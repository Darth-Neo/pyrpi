#!/usr/bin/env python
import os
import sqlite3


def determineTables(conn):
    print(u"Tables...")

    # Determine Table Names
    cursor = conn.cursor()
    cursor.execute(u"SELECT name FROM sqlite_master WHERE type='table';")
    for x in cursor.fetchall():
        print(u"%s" % x)


def printTemperatures(conn, barometer=False):
    if barometer is False:
        sel = u"select ReadingDateTime, TempF, Humidity from temperature_temperature order by id desc"
        column = u"Humidity"
    else:
        sel = u"select ReadingDateTime, TempF, Barometer from temperature_barometer order by id desc"
        column = u"Barometer"

    cursor = conn.execute(sel)

    for row in cursor:
        print(u"ReadingDateTime = %s\tTempf = %s\t %s = %s" %
              (row[0], row[1], column, row[2]))


if __name__ == u"__main__":

    bf = False
    home = u"/home/james.morris/PythonDev/Django/Weather"

    if bf is True:
        conn_str = home + os.sep + u"barometric_temp.db"
        conn = sqlite3.connect(conn_str)
    else:
        conn_str = home + os.sep + u"Weather.db"
        conn = sqlite3.connect(conn_str)

    print(u"Opened database successfully")

    # determineTables(conn)

    printTemperatures(conn, barometer=bf)

