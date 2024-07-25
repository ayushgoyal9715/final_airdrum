import asyncio
import csv
from datetime import datetime
from bleak import BleakClient

# Addresses to connect to
address1 = "C0:C5:68:C3:F8:BE"
address2 = "D7:2D:B7:4C:39:63"
MODEL_NBR_UUID = "00002a57-0000-1000-8000-00805f9b34fb"
CSV_FILE1 = "drum1.csv"
CSV_FILE2 = "drum2.csv"
READ_INTERVAL = 0.1

async def read_from_device(address, csv_file):
    while True:
        try:
            async with BleakClient(address) as client:
                print(f"Connected to device {address}")

                # Open the CSV file and set up the writer
                with open(csv_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    # Write the header only if the file is empty
                    if file.tell() == 0:
                        writer.writerow(["Timestamp", "acc_x", "acc_y", "acc_z", "GyroX", "GyroY", "GyroZ"])

                    while True:
                        try:
                            model_number = await client.read_gatt_char(MODEL_NBR_UUID)
                            model_number_str = model_number.decode('utf-8', errors='replace').strip()
                            print(f"Model Number from {address}: {model_number_str}")

                            # Split the sensor data into individual float values
                            values = model_number_str.split(",")
                            print(f"Values received from {address}: {values}")  # Log the values for debugging
                            if len(values) == 6:
                                try:
                                    accX, accY, accZ, gyroX, gyroY, gyroZ = map(float, values)
                                    # Write the data to the CSV file
                                    writer.writerow([datetime.now().isoformat(), accX, accY, accZ, gyroX, gyroY, gyroZ])
                                    file.flush()  # Ensure data is written to the file immediately
                                except ValueError as ve:
                                    print(f"ValueError: {ve} - could not convert data to float: {values}")
                            else:
                                print(f"Unexpected number of values received from {address}: {values}")
                        except Exception as e:
                            print(f"Error reading characteristic from {address}: {e}")
                        await asyncio.sleep(READ_INTERVAL)
        except Exception as e:
            print(f"Connection error with {address}: {e}")
        finally:
            print(f"Disconnected from device {address}")
            await asyncio.sleep(5)  # Wait before trying to reconnect

async def main():
    await asyncio.gather(
        read_from_device(address1, CSV_FILE1),
        read_from_device(address2, CSV_FILE2)
    )

asyncio.run(main())
