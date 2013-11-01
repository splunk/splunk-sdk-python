# coding=utf-8
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

import collections
import sys


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
