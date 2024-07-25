#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>

// Initialize the BNO055 sensor
Adafruit_BNO055 bno = Adafruit_BNO055(55);

void setup() {
  // Start serial communication for debugging
  Serial.begin(115200);   
  // Start serial communication for UART (Serial1)
  Serial1.begin(115200);  
  // Initialize I2C communication
  Wire.begin();           

  delay(1000);

  // Check if the sensor is connected
  if (!bno.begin()) {
    Serial.println("No BNO055 detected");
    while (1); // Halt if no sensor is detected
  } else {
    Serial.println("BNO055 detected");
  }

  bno.setExtCrystalUse(true) ;
  
  // Set the operation mode to NDOF (9 degrees of freedom)
  // bno.setMode(Adafruit_BNO055::OPERATION_MODE_NDOF);
}

void loop() {
  // Create a variable to store sensor events
  sensors_event_t linearAccelEvent, eulerEvent;

  // Get linear acceleration event
  bno.getEvent(&linearAccelEvent, Adafruit_BNO055::VECTOR_LINEARACCEL);

  // Get orientation event (Euler angles: yaw, pitch, roll)
  bno.getEvent(&eulerEvent, Adafruit_BNO055::VECTOR_EULER);

  // Prepare and send linear acceleration data over Serial1 (UART1)
  Serial1.print("Acc:");
  Serial1.print(linearAccelEvent.acceleration.x);
  Serial1.print(",");
  Serial1.print(linearAccelEvent.acceleration.y);
  Serial1.print(",");
  Serial1.print(linearAccelEvent.acceleration.z);
  Serial1.print("|");

  // Also print linear acceleration data to Serial (for debugging)
  Serial.print("Acc:");
  Serial.print(linearAccelEvent.acceleration.x);
  Serial.print(",");
  Serial.print(linearAccelEvent.acceleration.y);
  Serial.print(",");
  Serial.print(linearAccelEvent.acceleration.z);
  Serial.print("|");

  // Prepare and send orientation data (yaw, pitch, roll) over Serial1 (UART1)
  Serial1.print("Gyro:");
  Serial1.print(eulerEvent.orientation.x); // Yaw
  Serial1.print(",");
  Serial1.print(eulerEvent.orientation.y); // Pitch
  Serial1.print(",");
  Serial1.println(eulerEvent.orientation.z); // Roll

  // Also print orientation data to Serial (for debugging)
  Serial.print("Gyro:");
  Serial.print(eulerEvent.orientation.x); // Yaw
  Serial.print(",");
  Serial.print(eulerEvent.orientation.y); // Pitch
  Serial.print(",");
  Serial.println(eulerEvent.orientation.z); // Roll

  // Check calibration status
  uint8_t system, gyro, accel, mag;
  bno.getCalibration(&system, &gyro, &accel, &mag);

  // Print calibration status
  Serial.print("Calibration: SYS=");
  Serial.print(system, DEC);
  Serial.print(" GYR=");
  Serial.print(gyro, DEC);
  Serial.print(" ACC=");
  Serial.print(accel, DEC);
  Serial.print(" MAG=");
  Serial.println(mag, DEC);

  // Send calibration status over Serial1
  Serial1.print("Calibration: SYS=");
  Serial1.print(system, DEC);
  Serial1.print(" GYR=");
  Serial1.print(gyro, DEC);
  Serial1.print(" ACC=");
  Serial1.print(accel, DEC);
  Serial1.print(" MAG=");
  Serial1.println(mag, DEC);

  delay(100); // Adjust delay as needed for your application
}