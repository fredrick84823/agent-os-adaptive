import importlib

from ..utils import os
from .... import too_far

extra = importlib.import_module("app.plugins.extra")


def load(name):
    return importlib.import_module(name)
