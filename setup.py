#!/usr/bin/env python
#
# Copyright 2011-2012 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from distutils.core import setup, Command
import os, shutil, tarfile
import splunklib

def run_test_suite():
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    original_cwd = os.path.abspath(os.getcwd())
    os.chdir('tests')
    suite = unittest.defaultTestLoader.discover('.')
    unittest.TextTestRunner().run(suite)
    os.chdir(original_cwd)

class CoverageCommand(Command):
    """setup.py command to run code coverage of the test suite."""
    description = "Create an HTML coverage report from running the full test suite."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            import coverage
        except ImportError:
            print "Could not import coverage. Please install it and try again."
            exit(1)
        cov = coverage.coverage(source=['splunklib'])
        cov.start()
        run_test_suite()
        cov.stop()
        cov.html_report(directory='coverage_report')

class TestCommand(Command):
    """setup.py command to run the whole test suite."""
    description = "Run test full test suite."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        run_test_suite()

def get_python_files(files):
    """Utility function to get .py files from a list"""
    python_files = []
    for file_name in files:
        if file_name.endswith(".py"):
            python_files.append(file_name)

    return python_files

def setup_examples():
    """Function to create .spl files for modular input examples"""
    app_names = ["random_numbers", "github_forks"]

    splunklib_dir = "splunklib"
    modinput_dir = os.path.join(splunklib_dir, "modularinput")

    for app in app_names:
        spl = tarfile.open(os.path.join("build", app + ".spl"), "w")

        spl.add(
            os.path.join("examples", app, app + ".py"),
            arcname=os.path.join(app, "bin", app + ".py")
        )

        spl.add(
            os.path.join("examples", app, "default", "app.conf"),
            arcname=os.path.join(app, "default", "app.conf")
        )
        spl.add(
            os.path.join("examples", app, "README", "inputs.conf.spec"),
            arcname=os.path.join(app, "README", "inputs.conf.spec")
        )

        splunklib_files = get_python_files(os.listdir(splunklib_dir))
        for file_name in splunklib_files:
            spl.add(
                os.path.join(splunklib_dir, file_name),
                arcname=os.path.join(app, "bin", splunklib_dir, file_name)
            )

        modinput_files = get_python_files(os.listdir(modinput_dir))
        for file_name in modinput_files:
            spl.add(
                os.path.join(modinput_dir, file_name),
                arcname=os.path.join(app, "bin", modinput_dir, file_name)
            )

        spl.close()

setup(
    author="Splunk, Inc.",

    author_email="devinfo@splunk.com",

    cmdclass={'coverage': CoverageCommand,
              'test': TestCommand},

    description="The Splunk Software Development Kit for Python.",

    license="http://www.apache.org/licenses/LICENSE-2.0",

    name="splunk-sdk",

    packages = ["splunklib"],

    url="http://github.com/splunk/splunk-sdk-python",

    version=splunklib.__version__,

    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)

setup_examples()