#!/usr/bin/env python
#
# Copyright 2011-2013 Splunk, Inc.
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
from contextlib import closing
from fnmatch import fnmatch

import os
import splunklib
import tarfile

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

class DistCommand(Command):
    """setup.py command to create .spl files for modular input and search
    command examples"""
    description = "Build modular input and search command example .spl files."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def get_python_files(files):
        """Utility function to get .py files from a list"""
        python_files = []
        for file_name in files:
            if file_name.endswith(".py"):
                python_files.append(file_name)

        return python_files

    def run(self):
        # Create random_numbers.spl and github_forks.spl

        app_names = ['random_numbers', 'github_forks']
        splunklib_dir = "splunklib"
        modinput_dir = os.path.join(splunklib_dir, "modularinput")

        for app in app_names:
            with closing(tarfile.open(os.path.join("build", app + ".spl"), "w")) as spl:
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

                splunklib_files = self.get_python_files(os.listdir(splunklib_dir))
                for file_name in splunklib_files:
                    spl.add(
                        os.path.join(splunklib_dir, file_name),
                        arcname=os.path.join(app, "bin", splunklib_dir, file_name)
                    )

                modinput_files = self.get_python_files(os.listdir(modinput_dir))
                for file_name in modinput_files:
                    spl.add(
                        os.path.join(modinput_dir, file_name),
                        arcname=os.path.join(app, "bin", modinput_dir, file_name)
                    )

                spl.close()

        # Create searchcommands_app.spl

        sdk_dir = os.path.abspath('.')

        tarball = os.path.join(sdk_dir, 'build', 'searchcommands_app.spl')

        app_dir = os.path.join(sdk_dir, 'examples', 'searchcommands_app')
        arc_app_dir = 'searchcommands_app'

        lib_dir = os.path.join(sdk_dir, 'splunklib', 'searchcommands')
        arc_app_lib_dir = os.path.join(
            arc_app_dir, 'bin', 'splunklib', 'searchcommands')

        def exclude(path):
            basename = os.path.basename(path)
            result = (
                fnmatch(basename, '.DS_Store') or
                fnmatch(basename, '.idea') or
                fnmatch(basename, '*.py[co]') or
                fnmatch(basename, '*.log'))
            return result

        with tarfile.open(tarball, "w") as spl:
            spl.add(app_dir, arcname=arc_app_dir, exclude=exclude)
            spl.add(lib_dir, arcname=arc_app_lib_dir, exclude=exclude)


setup(
    author="Splunk, Inc.",

    author_email="devinfo@splunk.com",

    cmdclass={'coverage': CoverageCommand,
              'test': TestCommand,
              'dist': DistCommand},

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