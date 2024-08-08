
# MQTT Inverter Monitor for Voltronic inverters

- This script reads data from an inverter via a serial port and publishes the values to an MQTT server. It is designed to run periodically and can be set up as a systemd service for continuous operation.
- It is created for specific use with Voltronic Axpert MAX 7200 (or Axpert MAX 7.2k or Kodak, Solarpower or whatever chinese reselers name...)
- It extracts both MPPT trackers power.
- It have switching function between 2 serial ports, because my setup needs it (maybe issue inside inverter). You can simply insert same port to both config variables if you don't have same issues like me.

## Requirements

- Python 3.x
- `paho-mqtt` library
- `pyserial` library

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/mqtt-inverter-monitor.git
    cd mqtt-inverter-monitor
    ```

2. Install the required libraries:
    ```bash
    pip install paho-mqtt pyserial
    ```

3. Make the script executable:
    ```bash
    chmod +x mqtt_inverter.py
    ```

4. Move the script to a suitable location:
    ```bash
    sudo mv mqtt_inverter.py /usr/local/bin/
    ```

## Configuration

Edit the `mqtt_inverter.py` script to update the configuration variables at the top of the script:

```python
...

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

...
```

## Running as a Systemd Service

1. Create a systemd service file:

    ```bash
    sudo nano /etc/systemd/system/mqtt_inverter.service
    ```

2. Add the following content to the service file:

    ```ini
    [Unit]
    Description=MQTT Inverter Monitor Service
    After=network.target

    [Service]
    ExecStart=/usr/bin/python3 /usr/local/bin/mqtt_inverter.py
    WorkingDirectory=/usr/local/bin
    StandardOutput=inherit
    StandardError=inherit
    Restart=always
    User=root

    [Install]
    WantedBy=multi-user.target
    ```

3. Reload systemd to recognize the new service:

    ```bash
    sudo systemctl daemon-reload
    ```

4. Enable the service to start on boot:

    ```bash
    sudo systemctl enable mqtt_inverter.service
    ```

5. Start the service immediately:

    ```bash
    sudo systemctl start mqtt_inverter.service
    ```

6. Check the status of the service:

    ```bash
    sudo systemctl status mqtt_inverter.service
    ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

This project uses the following libraries:
- [paho-mqtt](https://www.eclipse.org/paho/)
- [pyserial](https://github.com/pyserial/pyserial)
