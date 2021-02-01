#!/usr/bin/env python3
import os
import sys
import json
import serial
from flask import Flask, request
import logging
from logging.config import dictConfig

config_file = os.path.join(os.path.dirname(__file__),
                '../config/serial-settings.json')

if not os.path.isfile(config_file):
    raise RuntimeError("Config file {0} not found".format(config_file))

with open(config_file) as f:
    config = json.load(f)
    print('Loaded config file {0}'.format(config_file))

dictConfig({
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


@app.route('/', methods=['POST'])
def handle_serial():
    request_json = request.get_json()
    app.logger.debug('Request JSON {0}'.format(request_json))

    with open(config_file) as f:
        config = json.load(f)
    
    log_level = 'ERROR'
    if u'device' not in request_json.keys():
        response = "FAILURE. Key 'device' not in JSON payload {0}".format(
            request_json)
    else:
        selected_device_name = request_json[u'device'].lower()

        if selected_device_name not in config['hdmi_devices_map']:
            response = "FAILURE. Requested device '{0}' not defined. Please " \
                "select from '{1}'".format(selected_device_name, 
                "', '".join(list(config['hdmi_devices_map'].keys())))
        else:
            selected_device_idx = config['hdmi_devices_map'][selected_device_name]
            serial_str_out = 'sw i0{0}\r\n'.format(selected_device_idx)

            try:
                with serial.Serial(
                        config['serial_device']['port'], 
                        config['serial_device']['baud'],
                        timeout=config['serial_device']['timeout']) as ser:
                    app.logger.debug('{0} Opened'.format(ser.portstr))
                    ser.write(str.encode(serial_str_out))
                    app.logger.info("SUCCESS - Wrote {0}".format(
                        repr(serial_str_out)))
                    response = "SUCCESS. Changed HDMI to device '{0}'".format(
                        selected_device_name)
                    log_level = 'INFO'
                app.logger.debug('{0} Closed'.format(ser.portstr))
            except serial.serialutil.SerialException as err:
                app.logger.error(err)
                response = 'FAILURE. Serial device not available'

    app.logger.log(getattr(logging, log_level), response)
    return response

if __name__ == '__main__':
    app.run(config['server']['IP'], config['server']['port'])
