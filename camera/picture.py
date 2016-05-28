#!/usr/bin/python
#
# Pi Camera Example Photo
#

import time
import picamera
from flask import Flask, redirect, url_for, abort

app = Flask(__name__)

@app.route('/index.html')
def getPicture():
    camera  = picamera.PiCamera()

    camera.hflip = True
    camera.vflip = True

    camera.capture('./image.jpg')

    return redirect('./index.html')

if __name__ == '__main__':
    # getPicture()
    app.run(host='0.0.0.0', debug=True)

