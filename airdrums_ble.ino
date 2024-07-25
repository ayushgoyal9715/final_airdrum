#include <bluefruit.h>

// Create BLE service and characteristics
BLEService sensorService = BLEService(0x180A); // Custom service UUID
BLECharacteristic sensorDataCharacteristic = BLECharacteristic(0x2A57); // UUID

void setup() {
  Serial.begin(115200);   // Initialize Serial for debugging
  Serial1.begin(115200);  // Initialize Serial1 for UART communication

  while (!Serial); // Wait for Serial to be ready
  Serial.println("NRF52840 Ready");

  // Begin BLE initialization
  Bluefruit.begin();
  Bluefruit.setName("NRF52840");
  Bluefruit.Periph.setConnectCallback(connect_callback);
  Bluefruit.Periph.setDisconnectCallback(disconnect_callback);

  // Configure and start the service
  sensorService.begin();

  // Configure and start the characteristic
  sensorDataCharacteristic.setProperties(CHR_PROPS_NOTIFY | CHR_PROPS_READ);
  sensorDataCharacteristic.setPermission(SECMODE_OPEN, SECMODE_NO_ACCESS);
  sensorDataCharacteristic.setFixedLen(40); // Set maximum length to 40 bytes
  sensorDataCharacteristic.begin();

  // Start advertising
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();
  Bluefruit.Advertising.addService(sensorService);
  Bluefruit.ScanResponse.addName();
  Bluefruit.Advertising.start(0); // 0 = Don't stop advertising automatically

  // Initialize characteristic value
  String initialValue = "0,0,0,0,0,0"; // Initial values for accelerometer and gyroscope
  sensorDataCharacteristic.write((uint8_t*)initialValue.c_str(), initialValue.length());

  Serial.println("BLE device active, waiting for connections...");
}

void loop() {
  // Listen for incoming BLE connections
  while (Bluefruit.connected()) {
    if (Serial1.available() > 0) {
      String data = Serial1.readStringUntil('\n'); // Read data until newline character

      // Split and process the data
      int accIndex = data.indexOf("Acc:");
      int gyroIndex = data.indexOf("Gyro:");

      if (accIndex != -1 && gyroIndex != -1) {
        String accData = data.substring(accIndex + 4, gyroIndex - 1);
        String gyroData = data.substring(gyroIndex + 5);

        // Parse accelerometer data
        int comma1 = accData.indexOf(',');
        int comma2 = accData.lastIndexOf(',');

        float accX = accData.substring(0, comma1).toFloat();
        float accY = accData.substring(comma1 + 1, comma2).toFloat();
        float accZ = accData.substring(comma2 + 1).toFloat();

        // Parse gyroscope data
        comma1 = gyroData.indexOf(',');
        comma2 = gyroData.lastIndexOf(',');

        float gyroX = gyroData.substring(0, comma1).toFloat();
        float gyroY = gyroData.substring(comma1 + 1, comma2).toFloat();
        float gyroZ = gyroData.substring(comma2 + 1).toFloat();

        // Print all values in one line, separated by commas
        String sensorData = String(accX, 2) + ", " + String(accY, 2) + ", " + String(accZ, 2) + ", " +
                            String(gyroX, 2) + ", " + String(gyroY, 2) + ", " + String(gyroZ, 2);

        Serial.println(sensorData);

        // Ensure the data length is within the allowed BLE characteristic length
        if (sensorData.length() <= 40) {
          // Send combined data over BLE
          sensorDataCharacteristic.notify((uint8_t*)sensorData.c_str(), sensorData.length());
        } else {
          Serial.println("Error: Sensor data length exceeds 40 bytes");
        }
      }
    }
    else Serial.println(Serial1.available());
  }
}

void connect_callback(uint16_t conn_handle) {
  // Connection callback
  Serial.println("Connected");
}

void disconnect_callback(uint16_t conn_handle, uint8_t reason) {
  // Disconnection callback
  Serial.println("Disconnected");
}