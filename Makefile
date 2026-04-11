PREFIX ?= /usr/local
BINDIR = $(PREFIX)/bin
APPDIR = $(PREFIX)/share/applications
CONFDIR = $(HOME)/.config/ovpn-launcher

.PHONY: install uninstall install-config dev clean

install:
	pip install --break-system-packages .
	install -Dm644 share/applications/ovpn-launcher.desktop $(APPDIR)/ovpn-launcher.desktop
	install -Dm644 share/icons/ovpn-launcher.svg $(PREFIX)/share/icons/ovpn-launcher.svg
	install -Dm644 share/icons/ovpn-launcher.svg $(PREFIX)/share/icons/hicolor/scalable/apps/ovpn-launcher.svg

uninstall:
	pip uninstall -y ovpn-launcher
	rm -f $(APPDIR)/ovpn-launcher.desktop
	rm -f $(PREFIX)/share/icons/ovpn-launcher.svg
	rm -f $(PREFIX)/share/icons/hicolor/scalable/apps/ovpn-launcher.svg

install-config:
	mkdir -p $(CONFDIR)/configs
	@if [ ! -f $(CONFDIR)/connections.conf ]; then \
		cp config/connections.conf.example $(CONFDIR)/connections.conf; \
		echo "Created $(CONFDIR)/connections.conf"; \
	else \
		echo "$(CONFDIR)/connections.conf already exists, skipping"; \
	fi

dev:
	pip install --break-system-packages -e .

clean:
	rm -rf build/ dist/ src/*.egg-info
