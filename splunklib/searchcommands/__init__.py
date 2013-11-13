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

""" Splunk search command library

#Design Notes

1. Command lines are constrained to this ABNF grammar::

       command       = command-name *[wsp option] *[wsp [dquote] field-name [dquote]]
       command-name  = alpha *( alpha / digit )
       option        = option-name [wsp] "=" [wsp] option-value
       option-name   = alpha *( alpha / digit / "_" )
       option-value  = word / quoted-string
       word          = 1*( %01-%08 / %0B / %0C / %0E-1F / %21 / %23-%FF ) ; Any character but DQUOTE and WSP
       quoted-string = dquote *( word / wsp / "\" dquote / dquote dquote ) dquote
       field-name    = ( "_" / alpha ) *( alpha / digit / "_" / "." / "-" )

   **Note:**

   This grammar is constrained to an 8-bit character set.

   **Note:**

   This grammar does not show that `field-name` values may be comma-separated
   when in fact they may be. This is because Splunk strips commas from the
   command line. A custom search command will never see them.

2. Commands support dynamic probing for settings.

   Splunk probes for settings dynamically when `supports_getinfo=true`.

3. Commands do not support static probing for settings.

   This module expects that commands are statically configured as follows::

       [<command-name>]
       filename = <command-name>.py
       supports_getinfo = true

   No other static configuration is required or expected and may interfere
   with command execution.

4. Commands do not support parsed arguments on the command line.

   Splunk parses arguments when `supports_rawargs=false`. This ``SearchCommand``
   class sets this value unconditionally. You cannot override it.

   **Rationale:**

   Splunk parses arguments by stripping quotes, nothing more. This may be useful
   in some cases, but doesn't work well with our chosen grammar.

5. Commands consume input headers.

   An input header is provided by Splunk when `enableheader=true`. The
   ``SearchCommand`` class sets this value unconditionally. You cannot override
   it.

6. Commands produce an output messages header.

   Splunk expects a command to produce an output messages header when
   `outputheader=true`. The ``SearchCommand`` class sets this value
   unconditionally. You cannot override it.

7. Commands support multi-value fields.

   Multi-value fields are provided and consumed by Splunk when
   `supports_multivalue=true`. The ``SearchCommand`` class sets this value
   unconditionally. You cannot override it.

8. Commands represent all fields on the output stream as multi-value fields.

   Splunk represents multi-value fields with a pair of fields:

   + `<field-name>`

     Contains the text from which the multi-value field was derived.

   + `__mv_<field-name>`

     Contains an encoded list. Values in the list are wrapped in dollar
     signs ('$') and separated by semi-colons (';). Dollar signs ('$')
     within a value are represented by a pair of dollar signs ('$$').
     Empty lists are represented by the empty string. Single-value lists
     are represented by the single value.

   On input this class processes and hides all **__mv_** fields. On output
   this class produces backing **__mv_** fields for all fields, thereby
   enabling a command to reduce its memory footprint by using streaming
   I/O. This is done at the cost of one extra byte of data per field per
   record on the output stream and extra processing time by the next
   processor in the pipeline.

9. A ReportingCommand may implement a `map` method (a.k.a, a streaming preop)
   and must implement a `reduce` operation (a.k.a., a reporting operation).

   Map/reduce command lines are distinguished by this module as exemplified
   here:

   **Command**::

       ...| sum total=total_date_hour date_hour

   **Reduce command line**::

       sum __GETINFO__ total=total_date_hour date_hour
       sum __EXECUTE__ total=total_date_hour date_hour

   **Map command line**::

       sum __GETINFO__ __map__ total=total_date_hour date_hour
       sum __EXECUTE__ __map__ total=total_date_hour date_hour

   The `__map__` argument is introduced by the `ReportingCommand._execute`
   method. ReportingCommand authors cannot influence the contents of the
   command line in this release.

#References

1. [Commands.conf.spec](http://docs.splunk.com/Documentation/Splunk/5.0.5/Admin/Commandsconf)
2. [Search command style guide](http://docs.splunk.com/Documentation/Splunk/6.0/Search/Searchcommandstyleguide)

"""
from __future__ import absolute_import

from .decorators import *
from .validators import *

from .generating_command import GeneratingCommand
from .reporting_command import ReportingCommand
from .streaming_command import StreamingCommand


def dispatch(command_class, argv=sys.argv, input_file=sys.stdin, output_file=
             sys.stdout, module_name=None):
    """ Instantiates and executes a search command class

    This function implements a [conditional script stanza](http://goo.gl/OFaox6)
    based on the value of `module_name`::

        if module_name is None or module_name == '__main__':
            # execute command

    If you would like this function's caller to act as either a reusable module
    or a standalone program, call it at module scope with `__name__` as the
    value of `module_name`. Otherwise, if you wish this function to
    unconditionally instantiate and execute `command_class`, pass `None` as the
    value of `module_name`.

    :param command_class: Class to instantiate and execute.
    :type command_class: ``.search_command.SearchCommand``
    :param argv: List of arguments to the command.
    :type argv: ``list``
    :param input_file: File from which the command will read data.
    :type input_file: ``file``
    :param output_file: File to which the command will write data.
    :type output_file: ``file``
    :param module_name: Name of the module calling dispatch or `None`.
    :type module_name: ``str``
    :returns: ``None``

    **Example**::

        #!/usr/bin/env python
        ...
        class CountMatchesCommand(StreamingCommand):
            ...

        dispatch(CountMatchesCommand, module_name=__name__)

    Dispatches the `CountMatchesCommand`, if and only if `__name__` is equal to
    `__main__`.

    """
    if module_name is not None and module_name != '__main__':
        return

    try:
        command_class().process(argv, input_file, output_file)
    except:
        import logging
        import traceback
        logging.fatal(traceback.format_exc())

    return
