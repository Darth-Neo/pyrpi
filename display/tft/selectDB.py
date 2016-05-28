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


def printReadings(conn):
    sel = u"select ReadingDateTime, TempF, Humidity, Barometer from temperature_temperature order by id desc"

    cursor = conn.execute(sel)

    for row in cursor:
        print(u"ReadingDateTime = %s\tTempf = %s\tHumidity = %s\tBarometer = %s" %
              (row[0], row[1], row[2], row[3]))


if __name__ == u"__main__":

    home = u"/home/pi/rpi/Weather"

    conn_str = home + os.sep + u"Weather.db"
    conn = sqlite3.connect(conn_str)

    print(u"Opened database successfully")

    # determineTables(conn)

    printReadings(conn)

