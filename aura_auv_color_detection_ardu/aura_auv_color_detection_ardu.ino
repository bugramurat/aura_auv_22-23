#include <Servo.h>  
// Sensor libraries
#include <Wire.h>
#include "MS5837.h"
MS5837 sensor;

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~esc n pwm~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Servo ESC_TOP_L, ESC_TOP_R, ESC_MID_L, ESC_MID_R, ESC_BOT_L, ESC_BOT_R; 

int PWM_STOP = 1500;
int PWM_HIGH = 1600;
int PWM_LOW = 1400;
int PWM_HIGH_MORE = 1780;
int PWM_LOW_MORE = 1320;
int PWM_HIGH_EXTREME = 1800;
int pwm_don = 1560;
int PWM_LOW_EXTREME = 1300;
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~esc n pwm~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~parameters~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
bool imGoing = false;
bool startVehicle = false;
int delay_sys = 5000;
float calculatedDepth = 0.80;
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~parameters~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

void setup() {
  Serial.begin(9600);
  
  // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~esc~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  ESC_TOP_L.attach(6);
  ESC_TOP_R.attach(9); 
  ESC_MID_L.attach(10); // Z-AXIS
  ESC_MID_R.attach(11); // Z-AXIS
  ESC_BOT_L.attach(3);
  ESC_BOT_R.attach(5);
  // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~esc~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  
  // Sensor setup----------------------------------------------------------------------
  Wire.begin();
  // Initialize pressure sensor
  // Returns true if initialization was successful
  // We can't continue with the rest of the program unless we can initialize the sensor
  while (!sensor.init()) {
    Serial.println("Init failed!");
    Serial.println("Are SDA/SCL connected correctly?");
    Serial.println("Blue Robotics Bar30: White=SDA, Green=SCL");
    Serial.println("\n\n\n");
    delay(delay_sys);
  }
  sensor.setModel(MS5837::MS5837_30BA);
  sensor.setFluidDensity(997); // kg/m^3 (freshwater, 1029 for seawater)
  //-----------------------------------------------------------------------------------
  delay(delay_sys);
}

void loop() {
  char c;

  // Sensor read
  sensor.read();
  
  if (Serial.available() > 0) {
    c = Serial.read();
    // Serial.println(c);
    runServo(c);
  }
  
  // Print sensor depth
  Serial.println(sensor.depth());
    // FIX THE AUV AT THE CALCULATED DEPTH  --23.06.2022
  if ((sensor.depth() > calculatedDepth) && imGoing == false && startVehicle == true){ // go up for fix the depth
    ESC_TOP_L.write(PWM_LOW_MORE);
    ESC_TOP_R.write(PWM_LOW_MORE);
    ESC_BOT_L.write(PWM_LOW_MORE);
    ESC_BOT_R.write(PWM_LOW_MORE);
  }
  else if((sensor.depth() < calculatedDepth) && imGoing == false && startVehicle == true){ // go down for fix the depth
    ESC_TOP_L.write(PWM_HIGH_MORE);
    ESC_TOP_R.write(PWM_HIGH_MORE);
    ESC_BOT_L.write(PWM_HIGH_MORE);
    ESC_BOT_R.write(PWM_HIGH_MORE);
  }
 
}

void runServo(char msg){
  if (msg=='2'){      // LEFT  --------------------------------------  LEFT
    ESC_MID_R.write(PWM_LOW_MORE);
    ESC_MID_L.write(PWM_STOP);
  }
  else if (msg=='3'){ // RIGHT   --------------------------------------   RIGHT
    ESC_MID_L.write(PWM_HIGH_MORE);
    ESC_MID_R.write(PWM_STOP);
  }
  else if (msg=='1'){ //   CENTER --------------------------------------   CENTER
    ESC_MID_L.write(PWM_HIGH_MORE);
    ESC_MID_R.write(PWM_LOW_MORE);
  }
  else if (msg=='5'){ //   SIT
    imGoing = true;
    
    // İLERİ GİT
    ESC_TOP_L.write(PWM_HIGH_MORE);
    ESC_TOP_R.write(PWM_HIGH_MORE);
    ESC_BOT_L.write(PWM_LOW_MORE);
    ESC_BOT_R.write(PWM_LOW_MORE);
    
    delay(3000);

    // OTUR
    ESC_TOP_L.write(PWM_STOP);
    ESC_TOP_R.write(PWM_STOP);
    ESC_BOT_L.write(PWM_STOP);
    ESC_BOT_R.write(PWM_STOP);
    ESC_MID_L.write(PWM_HIGH_MORE);
    ESC_MID_R.write(PWM_HIGH_MORE);
    
    delay(15000);

    // YUKARI AT
    ESC_TOP_L.write(PWM_STOP);
    ESC_TOP_R.write(PWM_STOP);
    ESC_BOT_L.write(PWM_STOP);
    ESC_BOT_R.write(PWM_STOP);
    ESC_MID_L.write(PWM_LOW_MORE);
    ESC_MID_R.write(PWM_LOW_MORE);

    delay(30000);
    
    imGoing = false;
  }
  else if(msg =='4'){
    ESC_TOP_L.write(PWM_STOP);
    ESC_TOP_R.write(PWM_STOP);
    ESC_BOT_L.write(PWM_STOP);
    ESC_BOT_R.write(PWM_STOP);
    ESC_MID_L.write(PWM_STOP);
    ESC_MID_R.write(PWM_STOP);
  }
  else if (msg=='7'){ // NULL
    ESC_MID_L.write(pwm_don);
    ESC_MID_R.write(pwm_don);
  }
  else if (msg=='8'){ // START AFTER DELAY
    delay(5000);
    startVehicle = true;
  }
}
