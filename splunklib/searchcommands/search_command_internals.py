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

import re
import collections
import urllib2 as urllib


class ConfigurationSettingsType(type):
    """ Metaclass for constructing ConfigurationSettings classes

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


class InputHeader(object):
    """ Represents a Splunk input header as a collection of name/value pairs

    TODO: Description

    """
    def __init__(self):
        self._settings = collections.OrderedDict()

    def __getitem__(self, name):
        return self._settings[name]

    def __iter__(self):
        for item in self._settings.items():
            yield item

    def __repr__(self):
        return ''.join(
            [InputHeader.__name__, '(', repr(self._settings.items()), ')'])

    def read(self, input_file):
        """ Reads an InputHeader from `input_file`

        The input header is read as a sequence of *<name>***:***<value>* pairs
        separated by a newline. The end of the input header is signalled by an
        empty line or an end-of-file.

        :param input_file: File-like object that supports iteration over lines

        """
        name = None
        for line in input_file:
            if line == '\n':
                break
            if line[-1] == '\n':
                line = line[:-1]
            value = line.split(':', 1)
            if len(value) == 2:
                name, value = value
                self._settings[name] = urllib.unquote(value)
            elif name is not None:
                # add new line to multi-line value
                self._settings[name] = '\n'.join(
                    [self._settings[name], urllib.unquote(line)])
            else:
                pass  # on unnamed multi-line value


class MessagesHeader(object):
    """ Represents an output messages header

    Messages in the header are of the form

        *<message-level>***=***<message-text>***\r\n**

    Message levels include:

        + info_message
        + warn_message
        + error_messages
        + TODO: ... (?)

    The end of the messages header is signalled by the occurrence of a single
    blank line (`\r\n').

    References:
    + [command.conf.spec](http://docs.splunk.com/Documentation/Splunk/6.0/Admin/Commandsconf#commands.conf.spec)

    """

    # TODO: Consider replacing this structure borrowed from Intersplunk
    # It is unsatisfying that it doesn't retain the full temporal order of
    # messages. You can see the order in which `info_message` level messages
    # arrived, but you cannot see how they interleaved with `warn_message` and
    # `error_message` level messages

    def __init__(self):
        self._messages = collections.OrderedDict(
            [('warn_message', []), ('info_message', []), ('error_message', [])])

    def __iadd__(self, level, text):
        self.append(level, text)

    def __iter__(self):
        for message_level in self._messages:
            for message_text in self._messages[message_level]:
                yield (message_level, message_text)

    def __repr__(self):
        messages = [message for message in self]
        return ''.join([MessagesHeader.__name__, '(', repr(messages), ')'])

    def append(self, level, text):
        """ Adds a message level/text pair to this MessagesHeader """
        if not level in self._messages.keys():
            raise ValueError('level="%s"' % level)
        self._messages[level].append(text)

    def write(self, output_file):
        """ Writes this MessageHeader to an output stream

        Messages are written as a sequence of *<message-level>***=**
        *<message-text>* pairs separated by '\r\n'. The sequence is terminated
        by a pair of '\r\n' sequences.

        """
        for level, message in self:
            output_file.write('%s=%s\r\n' % (level, message))
        output_file.write('\r\n')


class SearchCommandParser(object):
    """ Parses a search command line

    A search command line is described by the following syntax.

    **Syntax:**

    *<command-line>* ::= *<command>* (*<option>*)\* (*<field>*)\*

    *<command>* ::= *<name>*
    *<option>* ::= *<name>* <opt-whitespace> "=" <opt-whitespace> *<value>*
    *<field>* ::= *<name>*

    *<name>* ::= (*<letter>* | "_")(*<letter>* | *<digit>* | "_")\*
    *<value>* ::= (*<quoted-string>* | *<unquoted-string>*)
    *<quoted-string>* ::= '"' (*<any-character>* - '"' | *<escaped-quote>*)\*'"'
    *<unquoted-string>* ::= (*<any-character>* - ('"' | whitespace)
                            (*<any-character>* - ('"' | whitespace))\*

    *<escaped-quote>* ::= ('\"' | '""')

    **Example:**
    countmatches fieldname = word_count pattern = \w+ some_text_field

    Option names are mapped to properties in the targeted `SearchCommand`. It is
    the responsibility of the property setters to validate the values they
    receive. Property setters may also produce side effects. For example,
    setting the built-in log_level immediately changes the log_level.

    """

    # TODO: Finish BNF and ensure that regular expressions agree with it
    # One known point of departure: regular expressions and <name>

    # TODO: Consider an alternative to raising one error at a time. It would be
    # nice to get all ValueErrors (e.g., illegal values, missing options,...) in
    # one shot

    # TODO: Fix this bug: self.parse raises a SyntaxError when no options are
    # provided on the command line

    def parse(self, argv, command, fieldnames='ANY'):
        """ Splits an argument list into an options dictionary and a fieldname
        list

        The argument list must be of the form:

            [*<option-name>***=***<option-value>**]... [*<field-name>*]...

        Options names are validated against the list of `self.command` property
        names. Option values are validated by `self.command` property setters.
        Field names are checked against `fieldnames`.

        :param argv: List representing a search command line.
        :param fieldnames: List of valid field names, 'ANY', or None.
        :return: search_fieldnames, search_options. Options not included on the
        search command line are assigned a value of None.

        Exceptions:
        `SyntaxError`: Argument list is incorrectly formed.
        `ValueError`: Unrecognized option/field name, or an illegal field value.

        """
        # Get ready

        command_args = ' '.join(argv)
        command.fieldnames = None
        command.options.reset()

        command_args = SearchCommandParser._arguments_re.match(command_args)

        if command_args is None:
            raise SyntaxError("Syntax error: %s" % ' '.join(argv))

        # Parse options

        for option in SearchCommandParser._options_re.finditer(command_args.group('options')):
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

        selected_fields = command_args.group('fieldnames').split()

        if isinstance(fieldnames, str):
            if fieldnames != 'ANY':
                raise ValueError(
                    'Illegal argument to %s.parse method: fieldnames=%s' %
                    (type(self).__name__, fieldnames))
            command.fieldnames = selected_fields

        elif fieldnames:
            undefined_fields = []
            for name in selected_fields:
                if not name in fieldnames:
                    undefined_fields += [name]
            if len(undefined_fields) > 0:
                raise ValueError(
                    "Unrecognized field(s): %s" % ', '.join(undefined_fields))
            command.fieldnames = selected_fields

        elif len(selected_fields) > 0:
            raise ValueError(
                'Command does not accept field names, but %s found: %s' % (
                    'one was' if len(selected_fields) == 1 else 'some were',
                    ', '.join(selected_fields)))

        return

    @classmethod
    def unquote(cls, string):
        """ Removes quotes from a quoted string

        Splunk search command quote rules are applied. The enclosing
        double-quotes, if present, are removed. Escaped double-quotes ('\"' or
        '""') are replaced by a single double-quote ('"').

        **NOTE**

        We are not using a json.JSONDecoder because Splunk quote rules are
        different than JSON quote rules. A json.JSONDecoder does not recognize
        a pair of double-quotes ('""') as an escaped quote ('"') and will decode
        single-quoted strings ("'") in addition to double-quoted ('"') strings.

        """
        if string[0] == '"' and string[-1] == '"':
            string = string[1:-1]
        return re.sub(cls._escaped_quote_re, '"', string)

    #region Class variables

    _arguments_re = re.compile(r"""
        ^\s*
        (?P<options>  # Match a leading set of name/value pairs
            (?:
                (?:\w+)                             # keyword
                \s*=\s*                             # =
                (?:[^\s"]+|"(?:[^"]+|""|\\")*")\s*? # value
            )+
        )
        (?P<fieldnames> # Match a trailing set of (presumably) field names
            (?:\s+\w+)*
        )
        \s*$
        """, re.VERBOSE)

    _escaped_quote_re = re.compile(r"""(""|\\")""")

    _name_re = re.compile(r"""[_a-zA-Z][[_a-zA-Z0-9]+""")

    _options_re = re.compile(r"""
        # Captures a set of name/value pairs when used with re.finditer
        (\w+)                         # name
        \s*=\s*                       # =
        ([^\s"]+|"(?:[^"]+|""|\\")*") # value
        """, re.VERBOSE)

    #endregion
