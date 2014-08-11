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

"""

.. topic:: Design Notes

  1. Commands are constrained to this ABNF grammar::

        command       = command-name *[wsp option] *[wsp [dquote] field-name [dquote]]
        command-name  = alpha *( alpha / digit )
        option        = option-name [wsp] "=" [wsp] option-value
        option-name   = alpha *( alpha / digit / "_" )
        option-value  = word / quoted-string
        word          = 1*( %01-%08 / %0B / %0C / %0E-1F / %21 / %23-%FF ) ; Any character but DQUOTE and WSP
        quoted-string = dquote *( word / wsp / "\" dquote / dquote dquote ) dquote
        field-name    = ( "_" / alpha ) *( alpha / digit / "_" / "." / "-" )

     It is Constrained to an 8-bit character set. It does not show that
     :code:`field-name` values may be comma-separated. This is because Splunk strips
     commas from the command line. A search command will never see them.

  3. Commands must be statically configured as follows:

     .. code-block:: text
        :linenos:

        [commandname]
        filename = commandname.py
        supports_getinfo = true
        supports_rawargs = true

     No other static configuration is required or expected and may interfere with
     command execution.

  2. Commands support dynamic probing for settings.

     Splunk probes for settings dynamically when :code:`supports_getinfo=true`.
     You must add this line to the commands.conf stanza for each of your search
     commands.

  4. Commands do not support parsed arguments on the command line.

     Splunk parses arguments when :code:`supports_rawargs=false`. The
     :code:`SearchCommand` class sets this value unconditionally. You cannot
     override it.

     **Rationale**

     Splunk parses arguments by stripping quotes, nothing more. This may be useful
     in some cases, but doesn't work well with our chosen grammar.

  5. Commands consume input headers.

     An input header is provided by Splunk when :code:`enableheader=true`. The
     :class:`SearchCommand` class sets this value unconditionally. You cannot
     override it.

  6. Commands produce an output messages header.

     Splunk expects a command to produce an output messages header when
     :code:`outputheader=true`. The :class:`SearchCommand` class sets this value
     unconditionally. You cannot override it.

  7. Commands support multi-value fields.

     Multi-value fields are provided and consumed by Splunk when
     :code:`supports_multivalue=true`. This value is fixed. You cannot override
     it.

  8. This module represents all fields on the output stream in multi-value
     format.

     Splunk recognizes two kinds of data: :code:`value` and :code:`list(value)`.
     The multi-value format represents these data in field pairs. Given field
     :code:`name` the multi-value format calls for the creation of this pair of
     fields.

     ================= =========================================================
     Field name         Field data
     ================= =========================================================
     :code:`name`      Value or text from which a list of values was derived.

     :code:`__mv_name` Empty, if :code:`field` represents a :code:`value`;
                       otherwise, an encoded :code:`list(value)`. Values in the
                       list are wrapped in dollar signs ($) and separated by
                       semi-colons (;). Dollar signs ($) within a value are
                       represented by a pair of dollar signs ($$).
     ================= =========================================================

     Serializing data in this format enables streaming and reduces a command's
     memory footprint at the cost of one extra byte of data per field per record
     and a small amount of extra processing time by the next command in the
     pipeline.

  9. A :class:`ReportingCommand` must override :meth:`~ReportingCommand.reduce`
     and may override :meth:`~ReportingCommand.map`. Map/reduce commands on the
     Splunk processing pipeline are distinguished as this example illustrates.

     **Splunk command**

     .. code-block:: text

         sum total=total_date_hour date_hour

     **Map command line**

     .. code-block:: text

        sum __GETINFO__ __map__ total=total_date_hour date_hour
        sum __EXECUTE__ __map__ total=total_date_hour date_hour

     **Reduce command line**

     .. code-block:: text

        sum __GETINFO__ total=total_date_hour date_hour
        sum __EXECUTE__ total=total_date_hour date_hour

     The :code:`__map__` argument is introduced by
     :meth:`ReportingCommand._execute`. Search command authors cannot influence
     the contents of the command line in this release.

.. topic:: References

  1. `Search command style guide <http://docs.splunk.com/Documentation/Splunk/6.0/Search/Searchcommandstyleguide>`_

  2. `Commands.conf.spec <http://docs.splunk.com/Documentation/Splunk/5.0.5/Admin/Commandsconf>`_

"""

from __future__ import absolute_import

from .decorators import *
from .validators import *

from .generating_command import GeneratingCommand
from .reporting_command import ReportingCommand
from .streaming_command import StreamingCommand

if sys.platform == 'win32':
    # Work around the fact that on Windows '\n' is mapped to '\r\n'
    # The typical solution is to simply open files in binary mode, but stdout
    # is already open, thus this hack
    import msvcrt
    import os
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)


def dispatch(command_class, argv=sys.argv, input_file=sys.stdin, output_file=
             sys.stdout, module_name=None):
    """ Instantiates and executes a search command class

    This function implements a `conditional script stanza <http://goo.gl/OFaox6>`_
    based on the value of :code:`module_name`::

        if module_name is None or module_name == '__main__':
            # execute command

    Call this function at module scope with :code:`module_name=__name__`, if you
    would like your module to act as either a reusable module or a standalone
    program. Otherwise, if you wish this function to unconditionally instantiate
    and execute :code:`command_class`, pass :const:`None` as the value of
    :code:`module_name`.

    :param command_class: Class to instantiate and execute.
    :type command_class: :code:`SearchCommand`
    :param argv: List of arguments to the command.
    :type argv: :code:`list`
    :param input_file: File from which the command will read data.
    :type input_file: :code:`file`
    :param output_file: File to which the command will write data.
    :type output_file: :code:`file`
    :param module_name: Name of the module calling :code:`dispatch` or :const:`None`.
    :type module_name: :code:`str`
    :returns: :const:`None`

    **Example**

    .. code-block:: python
        :linenos:

        #!/usr/bin/env python
        from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators
        @Configuration()
        class SomeStreamingCommand(StreamingCommand):
            ...
            def stream(records):
                ...
        dispatch(SomeStreamingCommand, module_name=__name__)

    Dispatches the :code:`SomeStreamingCommand`, if and only if
    :code:`__name__` is equal to :code:`'__main__'`.


    **Example**

    .. code-block:: python
        :linenos:

        from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators
        @Configuration()
        class SomeStreamingCommand(StreamingCommand):
            ...
            def stream(records):
                ...
        dispatch(SomeStreamingCommand)

    Unconditionally dispatches :code:`SomeStreamingCommand`.

    """
    if module_name is None or module_name == '__main__':
        command_class().process(argv, input_file, output_file)
    return
