// This sketch uses the LDAC pin rather than I2C to 'output' the
// DAC's register value to the output pin. note that even if LDAC 
// isn't connected and toggled by a GPIO, if you continously
// write to the input register, you'll still get voltages on the
// output because the new value 'pushes' the old value out.
// So its more for synchronization than 'keeping the output from 
// changing'!
// in this demo we'll just write one value, 1.25V

//I2C device found at address 0x40  !
//I2C device found at address 0x4E  !

#include "Adafruit_AD569x.h"


Adafruit_AD569x ad5693; // Create an object of the AD5693 library
//
//    FILE: INA226_demo_plotter.ino
//  AUTHOR: Rob Tillaart
// PURPOSE: demo
//     URL: https://github.com/RobTillaart/INA226
//
// Can be used for IDE-Tools->Plotter


#include "INA226.h"
#include<string.h>

INA226 INA(0x40); // address 0x40 set by PCB

int v = 0;  // voltage


void setup() {
  Serial.begin(9600);   //start serial interface
  while (!Serial) delay(10); // Wait for serial port to start
  Serial.println("FSComm project, initialising");
  // Initialize the AD5693 chip
  if (ad5693.begin(0x4E, &Wire)) { // Address defined by PCB
    Serial.println("AD5693 initialization successful!");
  } else {
    Serial.println("Failed to initialize AD5693. Please check your connections.");
    while (1) delay(10); // Halt
  }

  // Reset the DAC
  ad5693.reset();

  // Configure the DAC for normal mode, internal reference, and no 2x gain
  if (ad5693.setMode(NORMAL_MODE, true, false)) {
    Serial.println("AD5693 a c");
  } else {
    Serial.println("Failed to configure AD5693.");
    while (1) delay(10); // Halt
  }

  Serial.println("Writing 1.25Vto output");
  
  if (!ad5693.writeDAC(0x4E)) {  // address 1001110 from PCB
    Serial.println("Failed to write to DAC");
    while (1) delay(10);
  }

// INA226

  Serial.println();
  Serial.println(__FILE__);
  Serial.print("INA226_LIB_VERSION: ");
  Serial.println(INA226_LIB_VERSION);
  Serial.println();

  Wire.begin();
  if (!INA.begin() )
  {
    Serial.println("could not connect. Fix and Reboot");
  }
}

void loop() {


  float bv = INA.getBusVoltage(); // Version 1 reads phodiode's resistor voltage, unprecise, use the next.
                                  // Version 2 reads the voltage of the amplifier, use to regulate it.

  float sv = INA.getShuntVoltage_uV();  // Reads voltage of the photodiode's resistor in microvolt.


  // CHECK THAT THE VOLTAGE IS ABOUT 1.25 (CHANGE ONLY THE VALUE BEFORE *32767.5)
  uint16_t value = (uint16_t)(1.0*32767.5);   // voltage of about 1.25V //0.92*... == 1.15 // 1.5*...=1.8V
                                              // precise correlation not found, change with caution.

  Serial.println(sv, 10);                     // prints shount voltage
  //Serial.print(bv, 3);                      // prints bus voltage
  //Serial.print("\t");
  //Serial.print(bv * cu, 3);
  //Serial.print("\t");
  //Serial.print((po - bv * cu), 3);
  delay(100);                                 // sets update time


// update DAC value
  ad5693.writeUpdateDAC(value);
  if (!ad5693.writeUpdateDAC(value)) {
    Serial.println("Failed to update DAC.");
  }
  else {
    /*Serial.println("Voltage of DAC set to: ");
    Serial.println(value);
    Serial.println();*/
  }

}