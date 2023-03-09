#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2011-2023 Splunk, Inc.
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

import os,sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import dispatch, ReportingCommand, Configuration, Option, validators


@Configuration(requires_preop=True)
class ReportingCSC(ReportingCommand):
    """
    The reportingapp command returns a count of students having higher total marks than cutoff marks.

    Example:

    ``| makeresults count=10 | eval math=random()%100, eng=random()%100, cs=random()%100 | reportingcsc cutoff=150 math eng cs``

    returns a count of students out of 10 having a higher total marks than cutoff.
    """

    cutoff = Option(require=True, validate=validators.Integer(0))

    @Configuration()
    def map(self, records):
        """returns a total marks of a students"""
        # list of subjects
        fieldnames = self.fieldnames
        for record in records:
            # store a total marks of a single student
            total = 0.0
            for fieldname in fieldnames:
                total += float(record[fieldname])
            yield {"totalMarks": total}

    def reduce(self, records):
        """returns a students count having a higher total marks than cutoff"""
        pass_student_cnt = 0
        for record in records:
            value = float(record["totalMarks"])
            if value >= float(self.cutoff):
                pass_student_cnt += 1
        yield {"student having total marks greater than cutoff ": pass_student_cnt}


dispatch(ReportingCSC, sys.argv, sys.stdin, sys.stdout, __name__)
