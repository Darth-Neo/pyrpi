/*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*  Initial date: Nov. 22, 2013
*  Last updated: Dec. 17, 2013
*
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This is a program for testing the RPi BrickPi drivers.
*/

#include "tick.h"
#include "BrickPi.h"

// Compile:
//   gcc -o program "Test BrickPi HW I2C HT Accel.c" -lrt
// Run:
//   sudo ./program

int result;

unsigned char I2C_Array_Out[1];
unsigned char I2C_Array_In[6];
int Accel_Values[3];

int main() {
  ClearTick();

  BrickPi.Address[0] = 1;
  BrickPi.Address[1] = 2;
  
  BrickPi.Timeout = 500;                       

  // Communication timeout (how long in ms since the last valid communication 
  // before floating the motors). 0 disables the timeout.

  result = BrickPiSetup();
  printf("BrickPiSetup: %dn", result);
  if(result)
    return 0;
 
  if(!result){
    I2C_Array_Out[0] = 0x42;
    while(1){
      result = I2C_WriteReadArray(0x02, 1, I2C_Array_Out, 6, I2C_Array_In);
      printf("I2C_WriteReadArray: %dn", result);
      if(!result){
        unsigned char i;
        for(i = 0; i < 3; i++){
          Accel_Values[i] = (I2C_Array_In[i] << 2) + (I2C_Array_In[i + 3] & 0x03);
          if(Accel_Values[i] >= 512){
            Accel_Values[i] = Accel_Values[i] - 1024;
          }
        }
        printf("X: %d   Y: %d   Z: %dn", Accel_Values[0], Accel_Values[1], Accel_Values[2]);
      }
      usleep(50000);
    }
  }
  return 0;
}
