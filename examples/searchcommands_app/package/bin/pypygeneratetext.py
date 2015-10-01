#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2011-2015 Splunk, Inc.
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

# Requirements:
# 1. PyPy is on splunkd's path.
#   Ensure this by performing these operating system-dependent tasks:
#
#   CentOS
#   ------
#   Create or update /etc/sysconfig/splunk with a line that looks like this:
#
#      1 PATH=$PATH:/opt/pypy/bin
#
#   P1 [ ] TODO: Verify that the instructions for putting PyPy on Splunk's PATH on CentOS work
#
#   OS X
#   ----
#   Edit /Library/LaunchAgents/com.splunk.plist and ensure that it looks like this:
#
#      1 <?xml version="1.0" encoding="UTF-8"?>
#      2 <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
#      3 <plist version="1.0">
#      4 <dict>
#      5     <key>Label</key>
#      6     <string>com.splunk</string>
#      7     <key>ProgramArguments</key>
#      8     <array>
#      9         <string>/Users/david-noble/Workspace/Splunk/bin/splunk</string>
#     10         <string>start</string>
#     11         <string>--no-prompt</string>
#     12         <string>--answer-yes</string>
#     13     </array>
#     14     <key>RunAtLoad</key>
#     15     <true/>
#     16     <key>EnvironmentVariables</key>
#     17     <dict>
#     18         <key>PATH</key>
#     19         <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/local/bin</string>
#     20     </dict>
#     21 </dict>
#     22 </plist>
#
#   Note lines 16-20 which extend PATH to include /opt/local/bin, the directory that the pypy executable is typically
#   placed.
#
#   Windows
#   -------
#   Ensure that pypy.exe is on the system-wide Path environment variable.

from __future__ import absolute_import, division, print_function, unicode_literals
import app

from splunklib.searchcommands import app_root, execute
from os import environ, path

import sys

pypy_argv = ['pypy', path.join(app_root, 'bin', 'generatetext.py')] + sys.argv[1:]
pypy_environ = dict(environ)
pypy_environ.pop('PYTHONPATH', None)  # On Windows Splunk is a 64-bit service, but pypy is a 32-bit program
pypy_environ.pop('DYLD_LIBRARY_PATH', None)  # On *nix Splunk includes shared objects that are incompatible with pypy

execute('pypy', pypy_argv, pypy_environ)
