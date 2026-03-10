VERSION := 0.4.2

# Application
APP_ROOT := $(CURDIR)

# Python
BUILDOUT_VERSION := 3.4
PYTHON ?= python
BUILDOUT ?= buildout
SUPERVISOR_CONF ?= $(HOME)/birdhouse/etc/supervisor/supervisord.conf
SUPERVISORD ?= supervisord
SUPERVISORCTL ?= supervisorctl

# Buildout files and folders
DOWNLOAD_CACHE := $(APP_ROOT)/downloads
BUILDOUT_FILES := parts eggs develop-eggs bin .installed.cfg .mr.developer.cfg *.egg-info *.bak.* $(DOWNLOAD_CACHE)

# end of configuration

.DEFAULT_GOAL := help

.PHONY: all
all: help

.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  help        to print this help message. (Default)"
	@echo "  version     to print version number of this Makefile."
	@echo "  install     to install app by running 'buildout -c custom.cfg'."
	@echo "  update      to update your application by running 'buildout -o -c custom.cfg' (buildout offline mode)."
	@echo "  clean       to delete all files that are created by running buildout."
	@echo "\nTesting targets:"
	@echo "  test        to run tests (but skip long running tests)."
	@echo "  testall     to run all tests (including long running tests)."
	@echo "  pep8        to run pep8 code style checks."
	@echo "\nSupporting targets:"
	@echo "  srcclean    to remove all *.pyc files."
	@echo "  distclean   to remove *all* files that are not controlled by 'git'. WARNING: use it *only* if you know what you do!"
	@echo "\nSupervisor targets:"
	@echo "  start       to start supervisor service."
	@echo "  stop        to stop supervisor service."
	@echo "  restart     to restart supervisor service."
	@echo "  status      to show supervisor status"

.PHONY: version
version:
	@echo "Version: $(VERSION)"

## Helper targets ... ensure that Makefile etc are in place

.PHONY: backup
backup:
	@echo "Backup custom config ..."
	@-test -f custom.cfg && cp -v --update --backup=numbered --suffix=.bak custom.cfg custom.cfg.bak

custom.cfg:
	@echo "Using custom.cfg for buildout ..."
	@test -f custom.cfg || cp -v custom.cfg.example custom.cfg

.PHONY: downloads
downloads:
	@echo "Using DOWNLOAD_CACHE $(DOWNLOAD_CACHE)"
	@test -d $(DOWNLOAD_CACHE) || mkdir -v -p $(DOWNLOAD_CACHE)

.PHONY: init
init: custom.cfg downloads

## Build targets

.PHONY: bootstrap
bootstrap: init
	@echo "Bootstrap buildout with pip ..."
	@$(PYTHON) -m pip install "setuptools<52" "zc.buildout==$(BUILDOUT_VERSION)"

.PHONY: install
install: bootstrap
	@echo "Installing application with buildout ..."
	@bash -c "$(BUILDOUT) -c custom.cfg"
	@echo "\nStart service with \`make start'"

.PHONY: update
update:
	@echo "Update application config with buildout (offline mode) ..."
	@bash -c "$(BUILDOUT) -o -c custom.cfg"

.PHONY: clean
clean: srcclean
	@echo "Cleaning buildout files ..."
	@-for i in $(BUILDOUT_FILES); do \
            test -e $$i && rm -v -rf $$i; \
        done

.PHONY: srcclean
srcclean:
	@echo "Removing *.pyc files ..."
	@-find $(APP_ROOT) -type f -name "*.pyc" -print | xargs rm

.PHONY: distclean
distclean: backup clean
	@echo "Cleaning distribution ..."
	@git diff --quiet HEAD || echo "There are uncommited changes! Not doing 'git clean' ..."
	@-git clean -dfx -e *.bak -e custom.cfg

.PHONY: test
test:
	@echo "Running tests (skip slow and online tests) ..."
	bash -c "bin/py.test -v -m 'not slow and not online'"

.PHONY: testall
testall:
	@echo "Running all tests (including slow and online tests) ..."
	bash -c "bin/py.test -v"

.PHONY: pep8
pep8:
	@echo "Running pep8 code style checks ..."
	flake8

## Supervisor targets

.PHONY: start
start:
	@echo "Starting supervisor service ..."
	$(SUPERVISORD) -c $(SUPERVISOR_CONF)

.PHONY: stop
stop:
	@echo "Stopping supervisor service ..."
	-$(SUPERVISORCTL) -c $(SUPERVISOR_CONF) shutdown

.PHONY: restart
restart:
	@echo "Restarting supervisor service ..."
	-$(SUPERVISORCTL) -c $(SUPERVISOR_CONF) shutdown
	@echo "Waiting for supervisor port to be released ..."
	@i=0; while [ $$i -lt 20 ]; do \
		if ! lsof -nP -iTCP:9001 -sTCP:LISTEN >/dev/null 2>&1; then break; fi; \
		sleep 1; \
		i=$$((i+1)); \
	done
	$(SUPERVISORD) -c $(SUPERVISOR_CONF)

.PHONY: status
status:
	@echo "Supervisor status ..."
	$(SUPERVISORCTL) -c $(SUPERVISOR_CONF) status
