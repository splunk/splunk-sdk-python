#!/usr/bin/env python

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
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
       pass

dispatch(%(command.title())Command, sys.argv, sys.stdin, sys.stdout, __name__)
