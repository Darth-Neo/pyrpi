#!/usr/bin/env python

import time
from datetime import datetime
from Logger import *

logger = setupLogging(u"lcd_ip")
logger.setLevel(INFO)

if __name__ == u"__main__":

    dts = u"%b %d  %I:%M %p"

    dt = datetime.now().strftime(u"%I:%M")
    hour = int(dt.split(u":")[0])
    minute = int(dt.split(u":")[1])

    logger.info(u"%s" % dt)

    dtMessageEncode = (datetime.now().strftime(dts))

    logger.info(u"%s" % dtMessageEncode)

    dtMessageDecode = time.strptime(dtMessageEncode, dts)

    month = dtMessageDecode.tm_mon
    day_of_month = dtMessageDecode.tm.mday
    hour = dtMessageDecode.tm_hour
    minutes = dtMessageDecode.tm_min
    day_start_of_year = dtMessageDecode.tm_yday

    logger.info(u"%s" % dtMessageDecode)

