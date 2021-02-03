# Voice Activated HDMI Switch

This project runs a flask webserver that accepts a POST request and will set the HDMI output of an IOGear HDMI Switch.

Requirements:
* IOGear HDMI Switch [tested with GHSW8241](https://www.iogear.com/product/GHSW8241/)
* USB to Serial RS232 Adapter [tested with Startech ICUSB2321F](https://www.startech.com/en-us/cards-adapters/icusb2321f)


Motivation. SmartTVs only have a limited number of HDMI ports. While some SmartTVs have their own APIs to programitcally change the active HDMI port, they are either not easy to use or cross-compatible across brands. I present a simple "plug-and-play" solution.

To change your HDMI switch's device mapping, do so in the [config file](/config/serial-settings.json#L2-L6)

To change your Serial device, do so in the [config file](/config/serial-settings.json#L9) or pass `--device /dev/ttyUSB<X>` to the script when running python from the shell.

Full list of acceptable serial commands for the IOGear HDMI Switch found in its manual [here](https://www.iogear.com/support/dm/download_manual/?mnid=1494).

## Running the server from shell
```bash
# Install requirements (conda or virtual env recommended)
python3 -m pip install requirements.txt
# Run the server
./pysrc/hdmi_switcher_server.py
```

## Running the server from DOCKER
```bash
# Build the image
docker build -t voice-hdmi-switch .
# Run the container
docker run -p 127.0.0.1:8080:8080/tcp --device /dev/ttyUSB<X>:/dev/ttyUSB<X> --privileged -t -i voice-hdmi-switch --device /dev/ttyUSB<X>
```

## POST to server using curl
```bash
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"device":"chromecast"}' \
  http://localhost:8080
```

## POST to server using [httpie](https://github.com/httpie/httpie)
```bash
http 127.0.0.1:8080 device=chromecast
```