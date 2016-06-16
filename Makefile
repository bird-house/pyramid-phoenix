VERSION := 0.3.0
RELEASE := develop

# Application
APP_ROOT := $(CURDIR)
APP_NAME := $(shell basename $(APP_ROOT))

# guess OS (Linux, Darwin, ...)
OS_NAME := $(shell uname -s 2>/dev/null || echo "unknown")
CPU_ARCH := $(shell uname -m 2>/dev/null || uname -p 2>/dev/null || echo "unknown")

# Python
SETUPTOOLS_VERSION=20.1.1
BUILDOUT_VERSION=2.5.0

# Anaconda 
ANACONDA_HOME ?= $(HOME)/anaconda
CONDA_ENV ?= $(APP_NAME)
CONDA_ENVS_DIR ?= $(HOME)/.conda/envs
CONDA_ENV_PATH := $(CONDA_ENVS_DIR)/$(CONDA_ENV)
PREFIX ?= $(HOME)/birdhouse

# Configuration used by update-config
HOSTNAME ?= localhost
USER ?= www-data
OUTPUT_PORT ?= 8090
LOG_LEVEL ?= WARN

# choose anaconda installer depending on your OS
ANACONDA_URL = http://repo.continuum.io/miniconda
ifeq "$(OS_NAME)" "Linux"
FN := Miniconda-latest-Linux-x86_64.sh
else ifeq "$(OS_NAME)" "Darwin"
FN := Miniconda-3.7.0-MacOSX-x86_64.sh
else
FN := unknown
endif

# Buildout files and folders
DOWNLOAD_CACHE := $(APP_ROOT)/downloads
BUILDOUT_FILES := parts eggs develop-eggs bin .installed.cfg .mr.developer.cfg *.egg-info bootstrap-buildout.py *.bak.* $(DOWNLOAD_CACHE)

# Docker
DOCKER_IMAGE := birdhouse/$(APP_NAME)
DOCKER_CONTAINER := $(APP_NAME)

# end of configuration

.DEFAULT_GOAL := help

.PHONY: all
all: help

.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  help        Prints this help message. (Default)"
	@echo "  version     Prints version number of this Makefile."
	@echo "  info        Prints information about your system."
	@echo "  install     Installs your application by running 'bin/buildout -c custom.cfg'."
	@echo "  update      Updates your application by running 'bin/buildout -o -c custom.cfg' (buildout offline mode)."
	@echo "  test        Run tests (but skip long running tests)."
	@echo "  testall     Run all tests (including long running tests)."
	@echo "  clean       Deletes all files that are created by running buildout."
	@echo "  srcclean    Removes all *.pyc files."
	@echo "  distclean   Removes *all* files that are not controlled by 'git'. WARNING: use it *only* if you know what you do!"
	@echo "  sysinstall  Installs system packages from requirements.sh. You can also call 'bash requirements.sh' directly."
	@echo "  passwd      Generate password for 'phoenix-password' in custom.cfg."
	@echo "  docs        Generates HTML documentation with Sphinx."
	@echo "  selfupdate  Updates this Makefile."
	@echo "\nSupervisor targets:"
	@echo "  start       Starts supervisor service: $(PREFIX)/etc/init.d/supervisord start"
	@echo "  stop        Stops supervisor service: $(PREFIX)/etc/init.d/supervisord stop"
	@echo "  restart     Restarts supervisor service: $(PREFIX)/etc/init.d/supervisord restart"
	@echo "  status      Supervisor status: $(PREFIX)/bin/supervisorctl status"
	@echo "\nDocker targets:"
	@echo "  Dockerfile  Generates a Dockerfile for this application."
	@echo "  dockerbuild Build a docker image for this application."

.PHONY: version
version:
	@echo "Version: $(VERSION)"

.PHONY: info
info:
	@echo "Informations about your Bird:"
	@echo "  OS_NAME             $(OS_NAME)"
	@echo "  CPU_ARCH            $(CPU_ARCH)"
	@echo "  Anaconda Home       $(ANACONDA_HOME)"
	@echo "  Conda Environment   $(CONDA_ENV). Use \`source activate $(CONDA_ENV)' to activate it."
	@echo "  Conda Prefix        $(CONDA_ENV_PATH)"
	@echo "  Installation Prefix $(PREFIX)"
	@echo "  APP_NAME            $(APP_NAME)"
	@echo "  APP_ROOT            $(APP_ROOT)"
	@echo "  DOWNLOAD_CACHE      $(DOWNLOAD_CACHE)"
	@echo "  DOCKER_IMAGE        $(DOCKER_IMAGE)"

## Helper targets ... ensure that Makefile etc are in place

.PHONY: backup
backup:
	@echo "Backup custom config ..." 
	@-test -f custom.cfg && cp -v --update --backup=numbered --suffix=.bak custom.cfg custom.cfg.bak

.PHONY: .gitignore
.gitignore:
	@echo "Setup default .gitignore ..."
	@curl "https://raw.githubusercontent.com/bird-house/birdhousebuilder.bootstrap/$(RELEASE)/dot_gitignore" --silent --insecure --output .gitignore 

.PHONY: bootstrap.sh
bootstrap.sh:
	@echo "Update bootstrap.sh ..."
	@curl "https://raw.githubusercontent.com/bird-house/birdhousebuilder.bootstrap/$(RELEASE)/bootstrap.sh" --silent --insecure --output bootstrap.sh "https://raw.githubusercontent.com/bird-house/birdhousebuilder.bootstrap/$(RELEASE)/bootstrap.sh"
	@chmod 755 bootstrap.sh

requirements.sh:
	@echo "Setup default requirements.sh ..."
	@curl "https://raw.githubusercontent.com/bird-house/birdhousebuilder.bootstrap/$(RELEASE)/requirements.sh" --silent --insecure --output requirements.sh 
	@chmod 755 requirements.sh

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

## Anaconda targets

.PHONY: anaconda
anaconda:
	@echo "Installing Anaconda ..."
	@test -d $(ANACONDA_HOME) || curl $(ANACONDA_URL)/$(FN) --silent --insecure --output "$(DOWNLOAD_CACHE)/$(FN)" 
	@test -d $(ANACONDA_HOME) || bash "$(DOWNLOAD_CACHE)/$(FN)" -b -p $(ANACONDA_HOME)   
	@echo "Add '$(ANACONDA_HOME)/bin' to your PATH variable in '.bashrc'."

.PHONY: conda_config
conda_config: anaconda
	@echo "Update ~/.condarc"
	@"$(ANACONDA_HOME)/bin/conda" config --add envs_dirs $(CONDA_ENVS_DIR)
	@"$(ANACONDA_HOME)/bin/conda" config --set ssl_verify false
	@"$(ANACONDA_HOME)/bin/conda" config --add channels defaults
	@"$(ANACONDA_HOME)/bin/conda" config --add channels birdhouse

.PHONY: conda_env
conda_env: anaconda conda_config
	@echo "Update conda environment $(CONDA_ENV) ..."
	@test -d $(CONDA_ENV_PATH) || "$(ANACONDA_HOME)/bin/conda" env create -n $(CONDA_ENV) -f environment.yml
	"$(ANACONDA_HOME)/bin/conda" install -y -n $(CONDA_ENV) setuptools=$(SETUPTOOLS_VERSION)

.PHONY: conda_pinned
conda_pinned: conda_env
	@echo "Update pinned conda packages ..."
	@test -d $(CONDA_ENV_PATH) && curl https://raw.githubusercontent.com/bird-house/birdhousebuilder.bootstrap/master/conda_pinned --silent --insecure --output "$(CONDA_ENV_PATH)/conda-meta/pinned" 

## Build targets

.PHONY: bootstrap
bootstrap: init conda_env conda_pinned bootstrap-buildout.py
	@echo "Bootstrap buildout ..."
	@test -f bin/buildout || bash -c "source $(ANACONDA_HOME)/bin/activate $(CONDA_ENV);python bootstrap-buildout.py -c custom.cfg --allow-site-packages --setuptools-version=$(SETUPTOOLS_VERSION) --buildout-version=$(BUILDOUT_VERSION)"

.PHONY: sysinstall
sysinstall:
	@echo "\nInstalling system packages for bootstrap ..."
	@bash bootstrap.sh -i
	@echo "\nInstalling system packages for your application ..."
	@test -f requirements.sh || bash requirements.sh

.PHONY: install
install: bootstrap
	@echo "Installing application with buildout ..."
	bash -c "source $(ANACONDA_HOME)/bin/activate $(CONDA_ENV);bin/buildout -c custom.cfg"
	@echo "\nStart service with \`make start'"

.PHONY: update
update:
	@echo "Update application config with buildout (offline mode) ..."
	bash -c "source $(ANACONDA_HOME)/bin/activate $(CONDA_ENV);bin/buildout -o -c custom.cfg"

.PHONY: update-config
update-config:
	@echo "Update application config with buildout (offline mode) and enviroment variables..."
	bash -c "source $(ANACONDA_HOME)/bin/activate $(CONDA_ENV);bin/buildout settings:hostname=$(HOSTNAME) settings:output-port=$(OUTPUT_PORT) settings:log-level=$(LOG_LEVEL) -o -c custom.cfg"

.PHONY: update-user
update-user:
	@echo "Update user permission on var/ ..."
	chown -R $(USER) $(PREFIX)/var && chown -R $(USER) $(PREFIX)/var/lib/.

.PHONY: clean
clean: srcclean
	@echo "Cleaning buildout files ..."
	@-for i in $(BUILDOUT_FILES); do \
            test -e $$i && rm -v -rf $$i; \
        done

.PHONY: srcclean
srcclean:
	@echo "Removing *.pyc files ..."
	@-find $(APP_ROOT) -type f -name "*.pyc" -print0 | xargs -0r rm

.PHONY: distclean
distclean: backup clean
	@echo "Cleaning distribution ..."
	@git diff --quiet HEAD || echo "There are uncommited changes! Not doing 'git clean' ..."
	@-git clean -dfx --exclude=*.bak

.PHONY: buildclean
buildclean:
	@echo "Removing bootstrap.sh ..."
	@test -e bootstrap.sh && rm -v bootstrap.sh

.PHONY: passwd
passwd: custom.cfg
	@echo "Generate Phoenix password ..."
	@echo "Enter a password with at least 8 characters."
	@bash -c "source $(ANACONDA_HOME)/bin/activate $(CONDA_ENV); python -c 'from IPython.lib import passwd; pw = passwd(algorithm=\"sha256\"); lines = [\"phoenix-password = \" + pw + \"\\n\" if line.startswith(\"phoenix-password\") else line for line in open(\"custom.cfg\", \"r\")]; file = open(\"custom.cfg\", \"w\"); file.writelines(lines); file.close()'"
	@echo ""
	@echo "Run \`make install restart' to activate this password." 

.PHONY: test
test:
	@echo "Running tests (skip slow and online tests) ..."
	bash -c "source $(ANACONDA_HOME)/bin/activate $(CONDA_ENV); bin/py.test -v -m 'not slow and not online'"

.PHONY: testall
testall:
	@echo "Running all tests (including slow and online tests) ..."
	bash -c "source $(ANACONDA_HOME)/bin/activate $(CONDA_ENV); bin/py.test -v"

.PHONY: docs
docs:
	@echo "Generating docs with Sphinx ..."
	$(MAKE) -C $@ clean linkcheck html
	@echo "open your browser: firefox docs/build/html/index.html"

.PHONY: selfupdate
selfupdate: bootstrap.sh requirements.sh .gitignore
	@curl "https://raw.githubusercontent.com/bird-house/birdhousebuilder.bootstrap/$(RELEASE)/Makefile" --silent --insecure --output Makefile 

## Supervisor targets

.PHONY: start
start:
	@echo "Starting supervisor service ..."
	$(PREFIX)/etc/init.d/supervisord start

.PHONY: stop
stop:
	@echo "Stopping supervisor service ..."
	$(PREFIX)/etc/init.d/supervisord stop

.PHONY: restart
restart:
	@echo "Restarting supervisor service ..."
	$(PREFIX)/etc/init.d/supervisord restart

.PHONY: status
status:
	@echo "Supervisor status ..."
	$(CONDA_ENV_PATH)/bin/supervisorctl -c ${PREFIX}/etc/supervisor/supervisord.conf status


## Docker targets

.PHONY: Dockerfile
Dockerfile: bootstrap
	@echo "Update Dockerfile ..."
	bin/buildout -c custom.cfg install docker

.PHONY: dockerrmi
dockerrmi: 
	@echo "Removing previous docker image ..."
	docker rmi $(DOCKER_IMAGE)

.PHONY: dockerbuild
dockerbuild: Dockerfile
	@echo "Building docker image ..."
	docker build --rm -t $(DOCKER_IMAGE) .

.PHONY: dockerrun
dockerrun: dockerbuild
	@echo "Run docker image ..."
	docker run -i -t -p 9001:9001 --name=$(DOCKER_CONTAINER) $(DOCKER_IMAGE) /bin/bash
