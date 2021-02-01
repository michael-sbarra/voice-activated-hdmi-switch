#!/usr/bin/env python3
import os
import sys
import json
import serial
from flask import Flask, request
import logging
from logging.config import dictConfig

config_file = os.path.join \
    (
        os.path.dirname(__file__),
        '../config/serial-settings.json'
    )

if not os.path.isfile(config_file):
    raise RuntimeError(f"Config file {config_file} not found")

with open(config_file) as f:
    config = json.load(f)
    print(f"Loaded config file {config_file}")

dictConfig \
({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)-7s %(module)-22s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': config['server']['logging_level'],
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

def format_keys(keys):
    return "'{0}'".format("', '".join(map(str, keys)))

@app.route('/', methods=['POST'])
def handle_serial():
    request_json = request.get_json()
    app.logger.debug(f"Request JSON {request_json}")

    with open(config_file) as f:
        config = json.load(f)

    log_level = 'ERROR'
    if u'device' not in request_json.keys():
        response = f"FAILURE. Key 'device' not in JSON payload {request_json}"
    else:
        selected_device_name = request_json[u'device'].lower()

        if selected_device_name not in config['hdmi_devices_map']:
            response = f"FAILURE. Requested device '{selected_device_name}' not defined. " \
                f"Please select from {format_keys(config['hdmi_devices_map'].keys())}"
        else:

            selected_device_idx = config['hdmi_devices_map'][selected_device_name]
            serial_str_out = f"sw i0{selected_device_idx}\r\n"

            device  = config['serial_device']['port']
            baud    = config['serial_device']['baud']
            timeout = config['serial_device']['timeout']

            try:
                with serial.Serial(device, baud, timeout=timeout) as ser:
                    app.logger.debug(f"{ser.portstr} Opened")
                    ser.write(str.encode(serial_str_out))
                    app.logger.info(f"SUCCESS - Wrote {serial_str_out!r}")
                    response = f"SUCCESS. Changed HDMI to device '{selected_device_name}'"
                    log_level = 'INFO'
                app.logger.debug(f"{ser.portstr} Closed")
            except serial.serialutil.SerialException as err:
                app.logger.error(err)
                response = "FAILURE. Serial device not available"

    app.logger.log(getattr(logging, log_level), response)
    return response

if __name__ == '__main__':
    app.run \
    (
        config['server']['IP'],
        config['server']['port']
    )
