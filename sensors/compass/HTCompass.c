/*
*  Jaikrishna
*  t.s.jaikrishna<at>gmail.com
*  Initial date:  	June 21, 2013
*  Updated : 		May 30, 2014
*  Modified by Steve Gale Sept 2012 to connect to hitechnic magnetic compass
* also based on Xander Soldaat's driver for this device
*  Based on Matthew Richardson's example on testing BrickPi drivers and Xander Soldaat's Example on NXT for RobotC
*  You may use this code as you wish, provided you give credit where it's due.
*  
*  This is a program for testing the RPi BrickPi drivers and I2C communication on the BrickPi with a dCompass on HMC5883L 
*
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# http://www.dexterindustries.com/
# This code is for testing the BrickPi with the Magnnetic Compass from Hitechnic 
# Product webpage: http://www.
*/

#include <stdio.h>
#include <math.h>
#include <time.h>
#include <math.h>
#include "tick.h"

#include <wiringPi.h>

#include "BrickPi.h"


#include <linux/i2c-dev.h>   
#include <fcntl.h>

// gcc -o program "Test BrickPi lib.c" -lrt -lm -L/usr/local/lib -lwiringPi
// gcc -o program "Test BrickPi lib.c" -lrt
// ./program

int result;



float angle;

#define PI 3.14159265359
#define I2C_PORT  PORT_2                             // I2C port for the dCompass
#define I2C_SPEED 0                                  // delay for as little time as possible. Usually about 100k baud

#define I2C_DEVICE_DCOM 0                        // DComm is device 0 on this I2C bus


int main() {
  int angleLow;
  int angleHigh;
  ClearTick();

  result = BrickPiSetup();
  printf("BrickPiSetup: %d\n", result);
  if(result)
    return 0;
  

  BrickPi.Address[0] = 1;
  BrickPi.Address[1] = 2;
  BrickPi.SensorType       [I2C_PORT]    = TYPE_SENSOR_I2C;
  BrickPi.SensorI2CSpeed   [I2C_PORT]    = I2C_SPEED;
  BrickPi.SensorI2CDevices [I2C_PORT]    = 1; // 1 device on bus?
  BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DCOM] = 0;  
  BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DCOM] = 0x02;	//0x02address for writing
  
  if(BrickPiSetupSensors())
    return 0;


  BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DCOM]    = 2;	//number of bytes to write
  BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DCOM]    = 2;	//number of bytes to read
  
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DCOM][0] = 0x41;	//mode command
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DCOM][1] = 0x00;	//measure command

  result = BrickPiSetupSensors();
  printf("BrickPiSetupSensors: %d\n", result);
  // device should be in measure mode 
  BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DCOM]    = 1;	//number of bytes to write
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DCOM][0] = 0x42;	//heading upper

  if(!result){
    printf("start of while loop\n");
    while(1){
      result = BrickPiUpdateValues();
      if(!result){        
          angleLow  = BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DCOM][0];
          angleHigh = BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DCOM][1];
          printf("Low: %d  High: %d  \n", angleLow,angleHigh);
        }
      }
      usleep(100000);
    }
  return 0;
}
