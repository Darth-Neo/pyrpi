#!/usr/bin/python

import sqlite3

MAX_ROWS = 24

def getTemperatures(conn):
    # ID = row[0] 
    # ReadingDateTime = row[1] 
    # TempC = row[2]
    # Tempf = row[3] 
    # Humidity = row[4]

    ins = "select * from temperature_temperature order by ID desc"
    cursor = conn.execute(ins)

    temps = [[x[0], x[1], x[3]] for x in cursor]    

    return temps


if __name__ == "__main__":
    conn = sqlite3.connect('/home/pi/rpi/Weather/Weather.db')

    temps = getTemperatures(conn)

    n = 0
    for temp in temps:
        print("%s : %s : %s" % (temp[0], temp[1][:-1], temp[2]))
        n += 1
        if n == MAX_ROWS:
            break



