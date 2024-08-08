
# MQTT Inverter Monitor

This script reads data from an inverter via a serial port and publishes the values to an MQTT server. It is designed to run periodically and can be set up as a systemd service for continuous operation.

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
INTERVAL = 15  # Interval in seconds
SERIAL_PORT_1 = "/dev/ttyUSB1"
SERIAL_PORT_2 = "/dev/ttyUSB2"
BAUD_RATE = 2400
MQTT_SERVER = "192.168.168.252"
MQTT_PORT = 1883
MQTT_USERNAME = "mosquit"
MQTT_PASSWORD = "mosquit"
MQTT_CLIENT_ID = "voltronic_bd8041d0cdf131a6ba4e5b3360b8bc5a"
TOPIC_QPIGS5 = "homeassistant/QPIGS5"
TOPIC_QPIGS2 = "homeassistant/QPIGS2"
TOPIC_INVERTER_POWER = "homeassistant/inverterPower"
TOPIC_PVIN = "homeassistant/PVin"
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
