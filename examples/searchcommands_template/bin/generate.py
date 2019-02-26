#!/usr/bin/env python

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import \
    dispatch, GeneratingCommand, Configuration, Option, validators

@Configuration()
class %(command.title())Command(GeneratingCommand):
    """ %(synopsis)

    ##Syntax

    %(syntax)

    ##Description

    %(description)

    """
    def generate(self):
       # Put your event  code here
       pass

dispatch(%(command.title())Command, sys.argv, sys.stdin, sys.stdout, __name__)
