VERSION := 0.4.0

# Application
APP_ROOT := $(CURDIR)

# Python
SETUPTOOLS_VERSION := 41
BUILDOUT_VERSION := 2.13.1

# Buildout files and folders
DOWNLOAD_CACHE := $(APP_ROOT)/downloads
BUILDOUT_FILES := parts eggs develop-eggs bin .installed.cfg .mr.developer.cfg *.egg-info bootstrap-buildout.py *.bak.* $(DOWNLOAD_CACHE)

# end of configuration

.DEFAULT_GOAL := help

.PHONY: all
all: help

.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  help        to print this help message. (Default)"
	@echo "  version     to print version number of this Makefile."
	@echo "  install     to install app by running 'bin/buildout -c custom.cfg'."
	@echo "  update      to update your application by running 'bin/buildout -o -c custom.cfg' (buildout offline mode)."
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

bootstrap-buildout.py:
	@echo "Update buildout bootstrap-buildout.py ..."
	@test -f boostrap-buildout.py || curl https://bootstrap.pypa.io/bootstrap-buildout.py --insecure --silent --output bootstrap-buildout.py

## Build targets

.PHONY: bootstrap
bootstrap: init bootstrap-buildout.py
	@echo "Bootstrap buildout ..."
	@test -f bin/buildout || bash -c "python bootstrap-buildout.py -c custom.cfg --allow-site-packages --setuptools-version=$(SETUPTOOLS_VERSION) --buildout-version=$(BUILDOUT_VERSION)"

.PHONY: install
install: bootstrap
	@echo "Installing application with buildout ..."
	@-bash -c "bin/buildout -c custom.cfg"
	@echo "\nStart service with \`make start'"

.PHONY: update
update:
	@echo "Update application config with buildout (offline mode) ..."
	@-bash -c "bin/buildout -o -c custom.cfg"

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
	bin/supervisord start

.PHONY: stop
stop:
	@echo "Stopping supervisor service ..."
	-bin/supervisord stop

.PHONY: restart
restart:
	@echo "Restarting supervisor service ..."
	bin/supervisord restart

.PHONY: status
status:
	@echo "Supervisor status ..."
	bin/supervisorctl status
