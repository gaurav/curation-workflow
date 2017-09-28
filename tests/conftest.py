"""
conftest.py: Sets up some fixtures to simplify test writing.
In this library, we mostly use this to prepare lists of files
that need processing.
"""

import pytest
import os
import fnmatch

phylorefs_path = "phylorefs"

def pytest_generate_tests(metafunc):
    """ 
    Add hooks for tests that need a parameterized list of 
    curated files to read.
    """

    dirs = [d for d in os.listdir(phylorefs_path) if os.path.isdir(phylorefs_path + "/" + d)]

    if "paper_json" in metafunc.fixturenames:
        metafunc.parametrize(
            "paper_json",
            [phylorefs_path + "/" + path + "/paper.json" for path in dirs]
        )

    if "labeled_json" in metafunc.fixturenames:
        metafunc.parametrize(
            "labeled_json",
            [phylorefs_path + "/" + path + "/labeled.json" for path in dirs]
        )
    
    if "paper_owl" in metafunc.fixturenames:
        metafunc.parametrize(
            "paper_owl",
            [phylorefs_path + "/" + path + "/paper.owl" for path in dirs]
        )
