APPDIR = /opt/inactivity-monitor
SERVICE_NAME="inactivity-monitor"

deploy:
	./deploy.sh

install:
	sudo $(APPDIR)/scripts/install_venv.sh

restart:
	sudo $(APPDIR)/scripts/restart.sh

status:
	sudo systemctl status $(SERVICE_NAME) --no-pager

run:
	/opt/inactivity-monitor/venv/bin/python /opt/inactivity-monitor/main.py

all: deploy install restart run