FROM python:latest

RUN pip install pyserial flask

ADD ./entrypoint.sh .
ADD ./pysrc/hdmi_switcher_server.py /pysrc/
ADD ./config/serial-settings.json /config/

ENTRYPOINT ["/entrypoint.sh"]

