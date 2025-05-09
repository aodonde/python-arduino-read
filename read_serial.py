import serial
import csv
from datetime import datetime
import pytz
import time
import math


def voltage_into_pH(delta: float, reference: float) -> float:
    #pH = 7 - Ein/S  
    #S = 59.16mV
    result = 7 - ((reference - delta)/59.16)

    return round(result,2)



max_record = 144


# Configuring the serial port
portal = serial.Serial()
portal.baudrate = 9600
portal.timeout = 1.1
portal.port = 'COM5' #Update with serial port name

portal.open()

if portal.is_open:
    print(f"Serial port {portal.name} is open.")
else:
    print(f"Failed to open the serial port.")

try:
    #If the port is open then create the file and header
    london_timezone = pytz.timezone('Europe/London')
    current_time = datetime.now(london_timezone)
    output_file = current_time.strftime('%d-%m-%Y_%H-%M-%S.csv')
    start_time = time.time()
    record_count = 0

    with open(output_file, 'w', newline='') as file:
        datalogger = csv.writer(file)
        datalogger.writerow(['Time', 'Sample','BLE Characteristic','Voltage (mV)', 'Calculated pH'])

        while record_count < max_record:
            print("Reading...")
            data_row = portal.readline().decode('utf-8').strip()
            data_list = data_row.split(',')

            if data_list[0].startswith('ttv'):
                record_count += 1
                adc_reading = float(data_list[1])
                adc_into_voltage = adc_reading / 1000
                ph_value = voltage_into_pH(adc_into_voltage,1.8)
                datalogger.writerow( [datetime.now(london_timezone).strftime("%H:%M:%S"), record_count, adc_reading, adc_into_voltage, ph_value])

except KeyboardInterrupt:
    print("Stopping the program")

except SystemExit:
    portal.close()

finally:
    portal.close()