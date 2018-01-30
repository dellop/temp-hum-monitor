# temp-hum-monitor
This script does the following using a Raspberry Pi:
1. Retrieves temperature, humidity and pressure data from a BME280 sensor.
2. Retrieves Honeywell thermostat information from Honeywell's online portal.
3. Runs two relays which turn on the humidifier when humidity is too low and also turns on the furnace fan at the same time.
4. All of this is uploaded to Thingspeak and to a local Mysql server.
