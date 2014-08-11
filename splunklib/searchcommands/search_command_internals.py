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

try:
    from collections import OrderedDict  # Python 2.7
except ImportError:
    from ordereddict import OrderedDict  # Python 2.6

import re
import urllib2 as urllib


class ConfigurationSettingsType(type):
    """ Metaclass for constructing ConfigurationSettings classes.

    Instances of the ConfigurationSettingsType construct ConfigurationSettings
    classes from a base ConfigurationSettings class and a dictionary of
    configuration settings. The settings in the dictionary are validated against
    the settings in the base class. You cannot add settings, you can only
    change their backing-field values and you cannot modify settings without
    backing-field values. These are considered fixed configuration setting
    values.

    This is an internal class used in two places:

    + decorators.Configuration.__call__

      Adds a ConfigurationSettings attribute to a SearchCommand class.

    + reporting_command.ReportingCommand.fix_up

      Adds a ConfigurationSettings attribute to a ReportingCommand.map method,
      if there is one.

    """
    def __new__(cls, module, name, bases, settings):
        cls = super(ConfigurationSettingsType, cls).__new__(
            cls, name, bases, {})
        return cls

    def __init__(cls, module, name, bases, settings):

        super(ConfigurationSettingsType, cls).__init__(name, bases, None)
        configuration_settings = cls.configuration_settings()

        for name, value in settings.iteritems():
            try:
                prop, backing_field = configuration_settings[name]
            except KeyError:
                raise AttributeError(
                    '%s has no %s configuration setting' % (cls, name))
            if backing_field is None:
                raise AttributeError(
                    'The value of configuration setting %s is managed' % name)
            setattr(cls, backing_field, value)

        cls.__module__ = module
        return


class InputHeader(object):
    """ Represents a Splunk input header as a collection of name/value pairs.

    """
    def __init__(self):
        self._settings = OrderedDict()

    def __getitem__(self, name):
        return self._settings[name]

    def __iter__(self):
        return self.iterkeys()

    def __len__(self):
        return len(self._settings)

    def __repr__(self):
        return ''.join(
            [InputHeader.__name__, '(', repr(self._settings.items()), ')'])

    def items(self):
        return self._settings.items()

    def iteritems(self):
        return self._settings.iteritems()

    def iterkeys(self):
        return self._settings.iterkeys()

    def itervalues(self):
        return self._settings.itervalues()

    def keys(self):
        return self._settings.keys()

    def values(self):
        return self._settings.values()

    def read(self, input_file):
        """ Reads an InputHeader from `input_file`.

        The input header is read as a sequence of *<key>***:***<value>* pairs
        separated by a newline. The end of the input header is signalled by an
        empty line or an end-of-file.

        :param input_file: File-like object that supports iteration over lines

        """
        key, value = None, None
        import sys
        for line in input_file:
            if line == '\n':
                break
            if line[-1:] == '\n':
                line = line[:-1]
            item = line.split(':', 1)
            if len(item) == 2:
                # start of a new item
                self._update(key, value)
                key, value = item[0], urllib.unquote(item[1])
            elif key is not None:
                # continuation of the current item
                value = '\n'.join([value, urllib.unquote(line)])

        self._update(key, value)
        return

    def _update(self, k, v):
        if k is not None:
            self._settings[k] = v
        return


class MessagesHeader(object):
    """ Represents an output messages header.

    Messages in the header are of the form

        *<message-level>***=***<message-text>***\r\n**

    Message levels include:

        + debug_message
        + info_message
        + warn_message
        + error_messages

    The end of the messages header is signalled by the occurrence of a single
    blank line (`\r\n').

    References:
    + [command.conf.spec](http://docs.splunk.com/Documentation/Splunk/6.0/Admin/Commandsconf#commands.conf.spec)

    """

    def __init__(self):
        self._messages = []

    def __iadd__(self, (message_level, message_text)):
        self._messages.append((message_level, message_text))
        return self

    def __iter__(self):
        return self._messages.__iter__()

    def __len__(self):
        return len(self._messages)

    def __repr__(self):
        return ''.join([MessagesHeader.__name__, '(', repr(self._messages), ')'])

    def append(self, message_level, message_text):
        """ Adds a message level/text pair to this MessagesHeader """
        if not message_level in MessagesHeader._message_levels:
            raise ValueError('message_level="%s"' % message_level)
        self._messages.append((message_level, message_text))

    def write(self, output_file):
        """ Writes this MessageHeader to an output stream.

        Messages are written as a sequence of *<message_text-message_level>***=**
        *<message_text-text>* pairs separated by '\r\n'. The sequence is
        terminated by a pair of '\r\n' sequences.

        """
        for message_level, message_text in self:
            output_file.write('%s=%s\r\n' % (message_level, message_text))
        output_file.write('\r\n')

    _message_levels = [
        'debug_message', 'warn_message', 'info_message', 'error_message']


class SearchCommandParser(object):
    """ Parses the arguments to a search command.

    A search command line is described by the following syntax.

    **Syntax**::

       command       = command-name *[wsp option] *[wsp [dquote] field-name [dquote]]
       command-name  = alpha *( alpha / digit )
       option        = option-name [wsp] "=" [wsp] option-value
       option-name   = alpha *( alpha / digit / "_" )
       option-value  = word / quoted-string
       word          = 1*( %01-%08 / %0B / %0C / %0E-1F / %21 / %23-%FF ) ; Any character but DQUOTE and WSP
       quoted-string = dquote *( word / wsp / "\" dquote / dquote dquote ) dquote
       field-name    = ( "_" / alpha ) *( alpha / digit / "_" / "." / "-" )

    **Note:**

    This syntax is constrained to an 8-bit character set.

    **Note:**

    This syntax does not show that `field-name` values may be comma-separated
    when in fact they can be. This is because Splunk strips commas from the
    command line. A custom search command will never see them.

    **Example:**
    countmatches fieldname = word_count pattern = \w+ some_text_field

    Option names are mapped to properties in the targeted ``SearchCommand``. It
    is the responsibility of the property setters to validate the values they
    receive. Property setters may also produce side effects. For example,
    setting the built-in `log_level` immediately changes the `log_level`.

    """
    def parse(self, argv, command):
        """ Splits an argument list into an options dictionary and a fieldname
        list.

        The argument list, `argv`, must be of the form::

            *[option]... *[<field-name>]

        Options are validated and assigned to items in `command.options`. Field
        names are validated and stored in the list of `command.fieldnames`.

        #Arguments:

        :param command: Search command instance.
        :type command: ``SearchCommand``
        :param argv: List of search command arguments.
        :type argv: ``list``
        :return: ``None``

        #Exceptions:

        ``SyntaxError``: Argument list is incorrectly formed.
        ``ValueError``: Unrecognized option/field name, or an illegal field value.

        """
        # Prepare

        command_args = ' '.join(argv)
        command.fieldnames = None
        command.options.reset()

        command_args = SearchCommandParser._arguments_re.match(command_args)

        if command_args is None:
            raise SyntaxError("Syntax error: %s" % ' '.join(argv))

        # Parse options

        for option in SearchCommandParser._options_re.finditer(
                command_args.group('options')):
            name, value = option.group(1), option.group(2)
            if not name in command.options:
                raise ValueError('Unrecognized option: %s = %s' % (name, value))
            command.options[name].value = SearchCommandParser.unquote(value)

        missing = command.options.get_missing()

        if missing is not None:
            if len(missing) == 1:
                raise ValueError('A value for "%s" is required' % missing[0])
            else:
                raise ValueError(
                    'Values for these options are required: %s' %
                    ', '.join(missing))

        # Parse field names

        command.fieldnames = command_args.group('fieldnames').split()
        command.logger.debug('%s: %s', type(command).__name__, command)
        return

    @classmethod
    def unquote(cls, string):
        """ Removes quotes from a quoted string.

        Splunk search command quote rules are applied. The enclosing
        double-quotes, if present, are removed. Escaped double-quotes ('\"' or
        '""') are replaced by a single double-quote ('"').

        **NOTE**

        We are not using a json.JSONDecoder because Splunk quote rules are
        different than JSON quote rules. A json.JSONDecoder does not recognize
        a pair of double-quotes ('""') as an escaped quote ('"') and will decode
        single-quoted strings ("'") in addition to double-quoted ('"') strings.

        """
        if len(string) == 0:
            return ''

        if string[0] != '"':
            return string

        if len(string) == 1:
            return string

        if string[-1] != '"':
            raise ValueError("Poorly formed string literal: %s" % string)

        def replace(match):
            value = match.group(0)
            if value == '\\\\':
                return '\\'
            if value == '\\"':
                return '"'
            if value == '""':
                return '"'
            if len(value) != 2:
                raise ValueError("Poorly formed string literal: %s" % string)
            return value  # consistent with python handling

        result = re.sub(cls._escaped_quote_re, replace, string[1:-1])
        return result

    #region Class variables

    _arguments_re = re.compile(r"""
        ^\s*
        (?P<options>    # Match a leading set of name/value pairs
            (?:
                (?:[_a-zA-Z][_a-zA-Z0-9]+)          # name
                \s*=\s*                             # =
                (?:[^\s"]+|"(?:[^"]+|""|\\")*")\s*? # value
            )*
        )
        \s*
        (?P<fieldnames> # Match a trailing set of field names
            (?:(?:[_a-zA-Z][_.a-zA-Z0-9-]+|"[_a-zA-Z][_.a-zA-Z0-9-]+")\s*)*
        )
        \s*$
        """, re.VERBOSE)

    _escaped_quote_re = re.compile(r"""(\\\\|\\"|""|\\."|\\)""")

    _name_re = re.compile(r"""[_a-zA-Z][[_a-zA-Z0-9]+""")

    _options_re = re.compile(r"""
        # Captures a set of name/value pairs when used with re.finditer
        ([_a-zA-Z][_a-zA-Z0-9]+)       # name
        \s*=\s*                        # =
        ([^\s"]+|"(?:[^"]+|""|\\")*")  # value
        """, re.VERBOSE)

    #endregion
