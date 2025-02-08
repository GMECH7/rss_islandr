# -*- coding: utf-8 -*-
import os
import sys

MODULE_PATH = os.path.dirname(__file__)

paths_in_project = (r".", r"assessment", r"core", r"data", r"data_readers")

for path in paths_in_project:
    sys.path.append(os.path.realpath(os.path.join(MODULE_PATH, path)))
