#!/usr/bin/env python

import sys
from splunklib.searchcommands import \
    dispatch, ReportingCommand, Configuration, Option, validators


@Configuration()
class %(command.title())Command(ReportingCommand):
    """ %(synopsis)

    ##Syntax

    %(syntax)

    ##Description

    %(description)

    """
    @Configuration()
    def map(self, events):
        # Put your streaming preop implementation here, or remove the map method,
        # if you have no need for a streaming preop
        pass

    def reduce(self, events):
        # Put your reporting implementation
        pass

dispatch(%(command.title())Command, sys.argv, sys.stdin, sys.stdout, __name__)
