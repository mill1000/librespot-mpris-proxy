TARGET_NAME ?= librespot-mpris-proxy
PREFIX ?= /usr/local

SYSTEMD_SERVICE_NAME ?= $(TARGET_NAME).service
SYSTEMD_POLICY_NAME ?= $(TARGET_NAME)-policy.conf

SYSTEMD_SERVICE_PATH ?= /etc/systemd/system
SYSTEMD_POLICY_PATH ?= /etc/dbus-1/system.d

MKDIR_P ?= mkdir -p

default:
	$(info Nothing to build. Run make install.)

install-systemd: $(SYSTEMD_SERVICE_NAME)
	cp -u $< $(SYSTEMD_SERVICE_PATH)
	systemctl daemon-reload
	systemctl enable $(SYSTEMD_SERVICE_NAME)
	systemctl start $(SYSTEMD_SERVICE_NAME)

install-bin: $(TARGET_NAME).py 
	@$(MKDIR_P) $(DESTDIR)$(PREFIX)/bin
	cp $< $(DESTDIR)$(PREFIX)/bin/${TARGET_NAME}
	chmod +x $(DESTDIR)$(PREFIX)/bin/${TARGET_NAME}

install-policy: $(SYSTEMD_POLICY_NAME)
	cp $< $(SYSTEMD_POLICY_PATH)/

install: install-bin install-policy install-systemd

uninstall-systemd:
	systemctl disable $(SYSTEMD_SERVICE_NAME)
	systemctl stop $(SYSTEMD_SERVICE_NAME)
	systemctl daemon-reload
	rm -f $(SYSTEMD_SERVICE_PATH)/$(SYSTEMD_SERVICE_NAME)

uninstall: uninstall-systemd
	rm -f $(DESTDIR)$(PREFIX)/bin/${TARGET_NAME}
	rm -f $(SYSTEMD_POLICY_PATH)/$(SYSTEMD_POLICY_NAME)