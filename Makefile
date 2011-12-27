PYTHON                   ?= ./ENV/bin/python

# Dev Django runserver variables
dev_webserver_ip         ?= 0.0.0.0
dev_webserver_port       ?= 8000

devserver:
	$(PYTHON) -m antler.manage runserver $(dev_webserver_ip):$(dev_webserver_port)

# assume there's no antler screen session already, and just make one from scratch
screen:
	screen -dmS antler
	screen -r antler -X source screenstart
	sleep 1
	screen -r antler
