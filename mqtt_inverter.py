import time
import serial
import paho.mqtt.client as mqtt
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration variables
INTERVAL = 10  # Refresh interval in seconds, 10s minimum
SERIAL_PORT_1 = "/dev/ttyUSB0"
SERIAL_PORT_2 = "/dev/ttyUSB0" # Second serial port, if you have disconnection problems and following changes in path. Can be the same as first one. (udev rules sucks...)
BAUD_RATE = 2400
MQTT_SERVER = "mqttServer"
MQTT_PORT = 1883
MQTT_USERNAME = "mqttUser"
MQTT_PASSWORD = "mqttPass"
MQTT_CLIENT_ID = "mqttClientID"
TOPIC_PV1 = "homeassistant/PV1power" # Topic for first MPPT tracker of Axpert 7.2kVA
TOPIC_PV2 = "homeassistant/PV2power" # Topic for second MPPT tracker of Axpert 7.2kVA
TOPIC_PVIN = "homeassistant/PVin" # Topic for sum of previous two values
TOPIC_INVERTER_POWER = "homeassistant/inverterPower" # Topic for inverter load in VA


# Function to read and decode response from serial port
def get_serial_response(command, serial_port):
    serial_port.write(command)
    response = serial_port.readlines(None)
    decoded_response = [line.decode('utf-8', errors='ignore') for line in response]
    response_str = ''.join(decoded_response)
    return response_str.strip().split()

# Function to clean and convert data to float
def clean_and_convert(data):
    try:
        return float(data.replace('(', '').replace(')', '').replace('\r', '').replace('\n', '').strip())
    except ValueError:
        return None

# Initialize MQTT client
mqtt_client = mqtt.Client(client_id=MQTT_CLIENT_ID)

# Set username and password
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Define on_connect callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT server successfully.")
    else:
        logging.error(f"Failed to connect to MQTT server, return code {rc}")

mqtt_client.on_connect = on_connect

try:
    mqtt_client.connect(MQTT_SERVER, MQTT_PORT, 60)
    mqtt_client.loop_start()
except Exception as e:
    logging.error(f"Failed to connect to MQTT server: {e}")
    exit(1)

# Main loop
while True:
    try:
        # Attempt to open the serial port
        try:
            serialport = serial.Serial(SERIAL_PORT_1, BAUD_RATE, timeout=0.5)
            logging.info(f"Serial port {SERIAL_PORT_1} opened successfully.")
        except serial.SerialException as e:
            logging.error(f"Failed to open serial port {SERIAL_PORT_1}: {e}")
            try:
                serialport = serial.Serial(SERIAL_PORT_2, BAUD_RATE, timeout=0.5)
                logging.info(f"Serial port {SERIAL_PORT_2} opened successfully.")
            except serial.SerialException as e:
                logging.error(f"Failed to open serial port {SERIAL_PORT_2}: {e}")
                time.sleep(INTERVAL)
                continue

        # Send the first command and get the response
        logging.info("Sending QPIGS command.")
        data_points_1 = get_serial_response(b"QPIGS 5\r", serialport)

        # Send the second command and get the response
        logging.info("Sending QPIGS2 command.")
        data_points_2 = get_serial_response(b"QPIGS2 5\r", serialport)

        result_1 = None
        result_2 = None

        # Ensure there are enough data points in the first response
        if len(data_points_1) >= 15:
            # Convert the values at positions 13 and 14 to floats for the first response
            value_13_1 = clean_and_convert(data_points_1[12])
            value_14_1 = clean_and_convert(data_points_1[13])
            if value_13_1 is not None and value_14_1 is not None:
                result_1 = round(value_13_1 * value_14_1)
                logging.info(f"PV1 power (W): {result_1}")
                mqtt_client.publish(TOPIC_PV1, result_1)
            else:
                logging.error("Error converting values in QPIGS response.")
            
            # Get and send the inverter power value
            inverter_power = clean_and_convert(data_points_1[4])
            if inverter_power is not None:
                inverter_power = round(inverter_power)
                logging.info(f"Inverter power (W): {inverter_power}")
                mqtt_client.publish(TOPIC_INVERTER_POWER, inverter_power)
            else:
                logging.error("Error converting inverter power value in QPIGS response.")
        else:
            logging.error(f"Unexpected number of data points in QPIGS response: {data_points_1}")

        # Ensure there are enough data points in the second response
        if len(data_points_2) >= 3:  # Adjust based on expected data points
            # Convert the values at positions 1 and 2 to floats for the second response
            value_1_2 = clean_and_convert(data_points_2[0])
            value_2_2 = clean_and_convert(data_points_2[1])
            if value_1_2 is not None and value_2_2 is not None:
                result_2 = round(value_1_2 * value_2_2)
                logging.info(f"PV2 power (W): {result_2}")
                mqtt_client.publish(TOPIC_PV2, result_2)
            else:
                logging.error("Error converting values in QPIGS2 response.")
        else:
            logging.error(f"Unexpected number of data points in QPIGS2 response: {data_points_2}")

        # Calculate and send PVin
        if result_1 is not None and result_2 is not None:
            PVin = result_1 + result_2
            logging.info(f"PVin - sum of both MPPTs (W): {PVin}")
            mqtt_client.publish(TOPIC_PVIN, PVin)
        else:
            logging.error("Unable to calculate PVin due to missing data.")

        # Close the serial port
        serialport.close()

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    # Wait for the next interval
    time.sleep(INTERVAL)

# Disconnect from MQTT (this line will never be reached in the infinite loop)
mqtt_client.disconnect()
logging.info("Disconnected from MQTT server.")
