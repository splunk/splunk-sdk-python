#!/usr/bin/env python
#
# Copyright 2011-2012 Splunk, Inc.
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

import logging
import random
import csv
import sys
import time

from splunklib.searchcommands import GeneratingCommand, Configuration, Option, validators


@Configuration(streaming=True, local=False)
class SimulateCommand(GeneratingCommand):
    """ Generates a sequence of events drawn from a CSV file using repeated random sampling

    ##Syntax

    simulate csv=<path> interval=<time-interval> rate=<expected-number-of-events>...

    ##Description

    ##Example

    ```
    simulate csv="/path/to/events.csv" interval=00:00:01 rate=200 runtime=00:00:30
    ```

    """
    csv_file = Option(doc='''
        **Syntax:** **csv=***<path>*
        **Description:** CSV file from which repeated random samples will be drawn''',
                      require=True, validate=validators.File())

    interval = Option(doc='''
        **Syntax:** **interval=***<time-interval>*
        **Description:** Event arrival interval''', require=True,
                      validate=validators.Duration())

    rate = Option(doc='''
        **Syntax:** **rate=***<expected-number-of-events-during-interval>*
        **Description:** Duration of simulation''', require=True,
                  validate=validators.Integer(1))

    runtime = Option(doc='''
        **Syntax:** **runtime=***<time-interval>*
        **Description:** Duration of simulation''', require=True,
                     validate=validators.Duration())

    def generate(self):
        """ Yields one random record at a time for the duration of the runtime """
        self.logger.debug('SimulateCommand: %s' % self)  # reports fully-formed command line
        if not self.records:
            self.records = [record for record in csv.DictReader(self.csv_file)]
            self.lambda_value = 1.0 / (self.rate / float(self.interval))
        while self.runtime > 0:
            count = long(round(random.expovariate(self.lambda_value)))
            start_time = time.clock()
            for record in random.sample(self.records, count):
                yield record
            interval = time.clock() - start_time
            if interval < self.interval:
                time.sleep(self.interval - interval)
            self.runtime -= max(interval, self.interval)
        return

    def __init__(self):
        super(SimulateCommand, self).__init__()
        self.lambda_value = None
        self.records = None


if __name__ == '__main__':
    try:
        SimulateCommand().process(sys.argv, sys.stdin, sys.stdout)
    except:
        import traceback
        logging.fatal(traceback.format_exc())
