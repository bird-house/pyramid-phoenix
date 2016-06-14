# -*- coding: utf-8 -*-

import pytest


# ``py.test --runslow`` causes the entire testsuite to be run, including test
# that are decorated with ``@@slow`` (scaffolding tests).
# see http://pytest.org/latest/example/simple.html#control-skipping-of-tests-according-to-command-line-option  # Noqa


## def pytest_addoption(parser):
##     parser.addoption("--runslow", action="store_true", help="run slow tests")


## slow = pytest.mark.skipif(
##     not pytest.config.getoption("--runslow"),
##     reason="need --runslow option to run"
## )
