# coding=utf-8
#
# Copyright © 2011-2015 Splunk, Inc.
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

from __future__ import absolute_import
from splunklib import six

from .script import Script
from .scheme import Scheme
from .argument import Argument

from inspect import getmembers

class InputItems(object):
    def __init__(self, scheme, inputs):
        self._scheme = scheme
        self._inputs = inputs

    def __iter__(self):
        for input_name, input_config in self._inputs.items():
            input = InputItem(self._scheme, input_config)
            yield [input_name, input]

class InputItem(object):
    def __init__(self, scheme, config):
        for name, value in config.items():
            for argument in scheme.arguments:
                if argument.name == name:
                    if argument.data_type == argument.data_type_boolean:
                        value = value.lower() not in ['n', 'no', 'f', 'false', '0']
                    elif argument.data_type == argument.data_type_number:
                        # assume float, as it can later be cast to int without issue
                        value = float(value)
            setattr(self, name, value)

class Configuration(object):
    """ Defines the configuration settings for a modular input.
    """
    def __init__(self, o=None, **kwargs):
        self._settings = kwargs

    def __call__(self, o):
        o.name = o.__name__
        o._settings = self._settings

        # called by Script.get_scheme (unless overridden)
        def decorated_get_scheme(fn_self):
            scheme = Scheme(fn_self.name)

            for setting_name, setting_value in fn_self._settings.items():
                setattr(scheme, setting_name, setting_value)

            for argument in fn_self._arguments:
                scheme.add_argument(argument)

            return scheme

        # called by Script.stream_events (unless overridden)
        def decorated_stream_events(fn_self, inputs, ew):
            input_items = InputItems(fn_self.get_scheme(), inputs.inputs)
            fn_self.preflight(input_items, ew)
            for input_name, input_config in input_items:
                fn_self.process_input(input_name, input_config, ew)
            fn_self.postflight(input_items, ew)
               
        setattr(o, 'decorated_get_scheme', decorated_get_scheme)
        setattr(o, 'decorated_stream_events', decorated_stream_events)

        is_configuration_setting = lambda attribute: isinstance(attribute, Argument)
        definitions = getmembers(o, is_configuration_setting)

        o._arguments = []
        for name, argument in definitions:
            if not argument.name:
                argument.name = name
            o._arguments.append(argument)

        return o
