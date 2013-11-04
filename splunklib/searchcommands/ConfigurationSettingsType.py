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


class ConfigurationSettingsType(type):
    """ TODO: Documentation

    """
    def __new__(cls, module, name, bases, settings):
        cls = super(ConfigurationSettingsType, cls).__new__(
            cls, name, bases, {})
        return cls

    def __init__(cls, module, name, bases, settings):
        # TODO: Attribute errors should report full class name, (e.g.,
        # SumCommand.ConfigurationSettings, not ConfigurationSettings
        # TODO: Deal with computed configuration settings
        # TODO: Deal with validation errors

        super(ConfigurationSettingsType, cls).__init__(name, bases, None)
        configuration_settings = cls.configuration_settings()

        for name, value in settings.iteritems():
            try:
                prop, backing_field = configuration_settings[name]
            except KeyError:
                raise AttributeError(
                    '%s has no %s setting' % (cls.__name__, name))
            if backing_field is None:
                raise AttributeError(
                    'Setting %s has fixed value %s', (name, getattr(cls, name)))
            setattr(cls, backing_field, value)

        cls.__module__ = module
        return
