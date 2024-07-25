#AirDrums Final Code
This folder contains the full code of the project Air Drums.
Connections:- Teensy 4.0 is connected to NRF15822(BLE 4.0) and BNO055

        Teensy to NRF15822(BLE 4.0) TX <--> RX
                                    RX <--> TX
                                   GND <--> GND
                                   Vin <--> Vin
                                   
        Teensy to BNO055           SDA <--> SDA
                                   SCL <--> SCL
                                   GND <--> GND
                                   Vin <--> Vcc
                                   
-> upload code on teensy to read and serve bno data via bluetooth
-> Take BNO readings on master device(laptop) via bluetooth connection 
                                   
                                   
