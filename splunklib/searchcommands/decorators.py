# Copyright 2011-2014 Splunk, Inc.
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

from inspect import getmembers, isclass, isfunction
from types import FunctionType, MethodType
from json import JSONEncoder

try:
    from collections import OrderedDict  # must be python 2.7
except ImportError:
    from ordereddict import OrderedDict  # must be python 2.6

from .search_command_internals import ConfigurationSettingsType
from .validators import OptionName


class Configuration(object):
    """ Defines the configuration settings for a search command.

    Documents, validates, and ensures that only relevant configuration settings
    are applied. Adds a :code:`name` class variable to search command classes
    that don't have one. The :code:`name` is derived from the name of the class.
    By convention command class names end with the word "Command". To derive
    :code:`name` the word "Command" is removed from the end of the class name
    and then converted to lower case for conformance with the `Search command
    style guide <http://docs.splunk.com/Documentation/Splunk/6.0/Search/Searchcommandstyleguide>`_

    """
    def __init__(self, **kwargs):
        self.settings = kwargs

    def __call__(self, o):
        if isfunction(o):
            # We must wait to finalize configuration as the class containing
            # this function is under construction at the time this call to
            # decorate a member function. This will be handled in the call to
            # o.ConfigurationSettings.fix_up(o), below.
            o._settings = self.settings
        elif isclass(o):
            name = o.__name__
            if name.endswith('Command'):
                name = name[:-len('Command')]
            o.name = name.lower()
            if self.settings is not None:
                o.ConfigurationSettings = ConfigurationSettingsType(
                    module='.'.join((o.__module__, o.__name__)),
                    name='ConfigurationSettings',
                    bases=(o.ConfigurationSettings,),
                    settings=self.settings)
            o.ConfigurationSettings.fix_up(o)
            Option.fix_up(o)
        else:
            raise TypeError(
                'Incorrect usage: Configuration decorator applied to %s'
                % (type(o), o.__name__))
        return o


class Option(property):
    """ Represents a search command option.

    Required options must be specified on the search command line.

    **Example:**

    Short form (recommended). When you are satisfied with built-in or custom
    validation behaviors.

    .. code-block:: python
        :linenos:

        total = Option(
            doc=''' **Syntax:** **total=***<fieldname>*
            **Description:** Name of the field that will hold the computed
            sum''',
            require=True, validate=validator.Fieldname())

    **Example:**

    Long form. Useful when you wish to manage the option value and its deleter/
    getter/setter side-effects yourself. You must provide a getter and a
    setter. If your :code:`Option` requires `destruction <http://docs.python.org/reference/datamodel.html#object.__del__>`_
    you must also provide a deleter. You must be prepared to accept a value of
    :const:`None` which indicates that your :code:`Option` is unset.

    .. code-block:: python
        :linenos:

        @Option()
        def logging_configuration(self):
            \""" **Syntax:** logging_configuration=<path>
            **Description:** Loads an alternative logging configuration file for
            a command invocation. The logging configuration file must be in
            Python ConfigParser-format. The *<path>* name and all path names
            specified in configuration are relative to the app root directory.

            \"""
            return self._logging_configuration

        @logging_configuration.setter
        def logging_configuration(self, value):
            if value is not None
                logging.configure(value)
                self._logging_configuration = value

        def __init__(self)
            self._logging_configuration = None

    """
    def __init__(self, fget=None, fset=None, fdel=None, doc=None, name=None,
                 default=None, require=None, validate=None):
        super(Option, self).__init__(fget, fset, fdel, doc)
        self.name = None if name is None else OptionName()(name)
        self.default = default
        self.require = bool(require)
        self.validate = validate

    def __call__(self, function):
        return self.getter(function)

    #region Methods

    @classmethod
    def fix_up(cls, command):

        is_option = lambda attribute: isinstance(attribute, Option)
        command.option_definitions = getmembers(command, is_option)
        member_number = 0

        for member_name, option in command.option_definitions:
            if option.name is None:
                option.name = member_name
            if option.fget is None and option.fset is None:
                field_name = '_' + member_name

                def new_getter(name):
                    def getter(self):
                        return getattr(self, name, None)
                    return getter

                fget = new_getter(field_name)
                fget = FunctionType(
                    fget.func_code, fget.func_globals, member_name, None,
                    fget.func_closure)
                fget = MethodType(fget, None, command)
                option = option.getter(fget)

                def new_setter(name):
                    def setter(self, value):
                        setattr(self, name, value)
                    return setter

                fset = new_setter(field_name)
                fset = FunctionType(
                    fset.func_code, fset.func_globals, member_name, None,
                    fset.func_closure)
                fset = MethodType(fset, None, command)
                option = option.setter(fset)

                setattr(command, member_name, option)
                command.option_definitions[member_number] = member_name, option
            member_number += 1
        return

    def deleter(self, function):
        deleter = super(Option, self).deleter(function)
        return self._reset(deleter, function)

    def getter(self, function):
        getter = super(Option, self).getter(function)
        return self._reset(getter)

    def setter(self, function):
        f = lambda s, v: function(s, self.validate(v) if self.validate else v)
        setter = super(Option, self).setter(f)
        return self._reset(setter)

    def _reset(self, other):
        other.name = self.name
        other.default = self.default
        other.require = self.require
        other.validate = self.validate
        return other

    #endregion

    #region Types

    class Encoder(JSONEncoder):
        def __init__(self, item):
            super(Option.Encoder, self).__init__()
            self.item = item

        def default(self, o):
            # Convert the value of a type unknown to the JSONEncoder
            validator = self.item.validator
            if validator is None:
                return str(o)
            return validator.format(o)

    class Item(object):
        """ Presents an instance/class view over a search command `Option`.

        """
        def __init__(self, command, option):
            self._command = command
            self._option = option
            self._is_set = False

        def __repr__(self):
            return str(self)

        def __str__(self):
            value = self.validator.format(self.value) if self.validator is not None else str(self.value)
            encoder = Option.Encoder(self)
            text = '='.join([self.name, encoder.encode(value)])
            return text

        #region Properties

        @property
        def is_required(self):
            return bool(self._option.require)

        @property
        def is_set(self):
            """ Indicates whether an option value was provided as argument.

            """
            return self._is_set

        @property
        def name(self):
            return self._option.name

        @property
        def validator(self):
            return self._option.validate

        @property
        def value(self):
            return self._option.__get__(self._command)

        @value.setter
        def value(self, value):
            self._option.__set__(self._command, value)
            self._is_set = True

        def reset(self):
            self._option.__set__(self._command, self._option.default)
            self._is_set = False

        #endif

    class View(object):
        """ Presents a view of the set of `Option` arguments to a search command.

        """
        def __init__(self, command):
            self._items = OrderedDict([
                (option.name, Option.Item(command, option))
                for member_name, option in type(command).option_definitions])
            return

        def __contains__(self, name):
            return name in self._items

        def __getitem__(self, name):
            return self._items[name]

        def __iter__(self):
            return self._items.__iter__()

        def __len__(self):
            return len(self._items)

        def __repr__(self):
            text = ''.join([
                'Option.View(',
                ','.join([repr(item) for item in self.itervalues()]),
                ')'])
            return text

        def __str__(self):
            text = ' '.join(
                [str(item) for item in self.itervalues() if item.is_set])
            return text

        #region Methods

        def get_missing(self):
            missing = [
                item.name for item in self._items.itervalues()
                if item.is_required and not item.is_set]
            return missing if len(missing) > 0 else None

        def iteritems(self):
            return self._items.iteritems()

        def iterkeys(self):
            return self.__iter__()

        def itervalues(self):
            return self._items.itervalues()

        def reset(self):
            for value in self.itervalues():
                value.reset()
            return

        #endif

    #endif
