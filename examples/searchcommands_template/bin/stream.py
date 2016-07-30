#!/usr/bin/env python

import sys
from splunklib.searchcommands import \
    dispatch, StreamingCommand, Configuration, Option, validators


@Configuration()
class %(command.title())Command(StreamingCommand):
    """ %(synopsis)

    ##Syntax

    %(syntax)

    ##Description

    %(description)

    """
    def stream(self, events):
       # Put your event transformation code here
       for event in events:
          yield event

dispatch(%(command.title())Command, sys.argv, sys.stdin, sys.stdout, __name__)
