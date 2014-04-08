#!/usr/bin/env python
#
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

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from splunklib.searchcommands import Configuration, StreamingCommand
from splunklib.client import Service
from cStringIO import StringIO
import os
import re
import sys

@Configuration()
class SearchCommand(StreamingCommand):

    def stream(self, records):
        value = 0
        for record in records:
            action = record['Action']
            if action == 'access_search_results_info':
                search_results_info = self.search_results_info
            if action == 'raise_error':
                raise RuntimeError('Testing')
            yield {'Data': value}
            value += 1
        return


class TestSearchCommand(unittest.TestCase):

    def setUp(self):
        super(TestSearchCommand, self).setUp()
        return

    def test_process(self):

        # Command.process should complain if supports_getinfo == False
        # We support dynamic configuration, not static

        expected = \
            '\r\n' \
            'ERROR,__mv_ERROR' \
            '\r\n' \
            'Command search appears to be statically configured and static configuration is unsupported by splunklib.searchcommands. Please ensure that default/commands.conf contains this stanza: [search] | filename = foo.py | supports_getinfo = true | supports_rawargs = true | outputheader = true,' \
            '\r\n'

        command = SearchCommand()
        result = StringIO()

        self.assertRaises(
            SystemExit, command.process, ['foo.py'], output_file=result)

        result.reset()
        observed = result.read()
        self.assertEqual(expected, observed)

        # Command.process should return configuration settings on Getinfo probe

        expected = \
            '\r\n' \
            'changes_colorder,clear_required_fields,enableheader,generating,local,maxinputs,needs_empty_results,outputheader,overrides_timeorder,passauth,perf_warn_limit,required_fields,requires_srinfo,retainsevents,run_in_preview,stderr_dest,streaming,supports_multivalues,supports_rawargs,__mv_changes_colorder,__mv_clear_required_fields,__mv_enableheader,__mv_generating,__mv_local,__mv_maxinputs,__mv_needs_empty_results,__mv_outputheader,__mv_overrides_timeorder,__mv_passauth,__mv_perf_warn_limit,__mv_required_fields,__mv_requires_srinfo,__mv_retainsevents,__mv_run_in_preview,__mv_stderr_dest,__mv_streaming,__mv_supports_multivalues,__mv_supports_rawargs\r\n' \
            '1,0,1,0,0,0,1,1,0,0,0,,0,1,1,log,1,1,1,,,,,,,,,,,,,,,,,,,\r\n'

        command = SearchCommand()
        result = StringIO()
        command.process(['foo.py', '__GETINFO__'], output_file=result)
        result.reset()
        observed = result.read()
        self.assertEqual(expected, observed)

        # Command.process should produce an error record on parser errors, if
        # invoked to get configuration settings

        expected = \
            '\r\n' \
            'ERROR,__mv_ERROR\r\n' \
            'Unrecognized option: undefined_option = value,\r\n'

        command = SearchCommand()
        result = StringIO()

        self.assertRaises(SystemExit, command.process, ['foo.py', '__GETINFO__', 'undefined_option=value'], output_file=result)
        result.reset()
        observed = result.read()
        self.assertEqual(expected, observed)

        # Command.process should produce an error message and exit on parser
        # errors, if invoked to execute

        expected = \
            '\r\n' \
            'ERROR,__mv_ERROR\r\n' \
            'Unrecognized option: undefined_option = value,\r\n'

        command = SearchCommand()
        result = StringIO()

        try:
            command.process(args=['foo.py', '__EXECUTE__', 'undefined_option=value'], input_file=StringIO('\r\n'), output_file=result)
        except SystemExit as e:
            result.reset()
            observed = result.read()
            self.assertNotEqual(e.code, 0)
            self.assertEqual(expected, observed)
        except BaseException as e:
            self.fail("Expected SystemExit, but caught %s" % type(e))
        else:
            self.fail("Expected SystemExit, but no exception was raised")

        # Command.process should exit on processing exceptions

        expected = \
            '\r\n' \
            'ERROR,__mv_ERROR\r\n' \
            '\'NoneType\' object is not iterable,\r\n'

        command = SearchCommand()
        result = StringIO()

        try:
            command.process(args=['foo.py', '__EXECUTE__'], input_file=StringIO('\r\nAction\r\nraise_error'), output_file=result)
        except SystemExit as e:
            result.reset()
            observed = result.read()
            self.assertNotEqual(e.code, 0)
            self.assertEqual(expected, observed)
        except BaseException as e:
            self.fail("Expected SystemExit, but caught %s" % type(e))
        else:
            self.fail("Expected SystemExit, but no exception was raised")

        # Command.process should provide access to search results info

        python_version = 10 * sys.version_info[0] + sys.version_info[1]

        expected = \
            '''SearchResultsInfo(sid=1391366014.3, timestamp=1391366014.757223, now=1391366014, setStart=1391366007, index_et=1391366011, index_lt=1391366011, startTime=1386621222, rt_earliest=None, rt_latest=None, rtspan=None, scan_count=0, drop_count=0, maxevents=0, countMap={'in_ct.command.fields': 76, 'duration.command.search': 13, 'invocations.startup.handoff': 1, 'duration.dispatch.results_combiner': 1, 'invocations.command.search.kv': 1, 'duration.dispatch.stream.local': 14, 'out_ct.command.head': 10, 'invocations.command.search.rawdata': 1, 'invocations.dispatch.results_combiner': 1, 'invocations.command.fields': 1, 'out_ct.command.search.typer': 76, 'invocations.dispatch.writeStatus': 3, 'invocations.command.search.index': 1, 'duration.command.head': 1, 'duration.dispatch.evaluate': 130, 'duration.dispatch.evaluate.search': 41, 'in_ct.command.search.calcfields': 76, 'duration.dispatch.writeStatus': 3, 'invocations.command.search.tags': 1, 'in_ct.command.search.lookups': 76, 'duration.command.search.tags': 1, 'duration.command.search.lookups': 1, 'invocations.dispatch.evaluate': 1, 'duration.command.fields': 1, 'invocations.command.search.summary': 1, 'duration.dispatch.evaluate.countmatches': 88, 'out_ct.command.prehead': 10, 'in_ct.command.search.typer': 76, 'out_ct.command.search.calcfields': 76, 'invocations.command.head': 1, 'duration.startup.handoff': 39, 'duration.command.search.rawdata': 2, 'duration.command.search.index.usec_1_8': 0, 'invocations.command.search.fieldalias': 1, 'duration.dispatch.createProviderQueue': 27, 'duration.dispatch.fetch': 14, 'out_ct.command.search.tags': 76, 'duration.command.search.typer': 4, 'in_ct.command.head': 10, 'invocations.dispatch.createProviderQueue': 1, 'out_ct.command.fields': 76, 'invocations.dispatch.evaluate.head': 1, 'out_ct.command.search.fieldalias': 76, 'invocations.command.search.typer': 1, 'duration.dispatch.check_disk_usage': 1, 'out_ct.command.search': 76, 'in_ct.command.search': 0, 'invocations.dispatch.fetch': 1, 'duration.command.search.index': 1, 'duration.command.search.summary': 1, 'in_ct.command.search.tags': 76, 'duration.dispatch.evaluate.head': 1, 'duration.command.search.kv': 7, 'invocations.command.search.calcfields': 1, 'duration.command.search.fieldalias': 1, 'invocations.dispatch.evaluate.countmatches': 1, 'in_ct.command.search.fieldalias': 76, 'invocations.command.search': 1, 'invocations.dispatch.stream.local': 1, 'duration.command.search.calcfields': 1, 'invocations.dispatch.check_disk_usage': 1, 'prereport_events': 0, 'invocations.dispatch.evaluate.search': 1, 'invocations.command.search.index.usec_1_8': 7, 'duration.command.prehead': 1, 'invocations.command.prehead': 1, 'invocations.command.search.lookups': 1, 'out_ct.command.search.lookups': 76, 'in_ct.command.prehead': 76}, columnOrder=None, keySet='index::_internal', remoteServers=None, is_remote_sorted=1, rt_backfill=0, read_raw=1, enable_event_stream=1, rtoptions=None, field_rendering=None, query_finished=1, request_finalization=0, auth_token='9ce2897f792c52a6ecdcd2e03aa4677c', splunkd_port=8089, splunkd_protocol='https', splunkd_uri='https://127.0.0.1:8089', internal_only=0, summary_mode='none', summary_maxtimespan=None, summary_stopped=0, is_batch_mode=0, root_sid=None, shp_id='A8797F6F-B6BF-43E9-9AFE-857D2FBC8534', search='search index=_internal | head 10 | countmatches fieldname=word_count pattern=\\\\\\\w+ uri', remote_search='litsearch index=_internal | fields  keepcolorder=t "*" "_bkt" "_cd" "_si" "host" "index" "linecount" "source" "sourcetype" "splunk_server" "uri,word_count" | prehead  limit=10 null=false keeplast=false', reduce_search=None, datamodel_map=None, tstats_reduce=None, normalized_search='litsearch index=_internal | fields keepcolorder=t "*" "_bkt" "_cd" "_si" "host" "index" "linecount" "source" "sourcetype" "splunk_server" "uri,word_count" | prehead limit=10 null=false keeplast=false', summary_id='A8797F6F-B6BF-43E9-9AFE-857D2FBC8534_searchcommands_app_admin_013dda14f276a384', normalized_summary_id='A8797F6F-B6BF-43E9-9AFE-857D2FBC8534_searchcommands_app_admin_NS91c147524d89ae5a', generation_id=0, label=None, is_saved_search=0, realtime=0, indexed_realtime=0, indexed_realtime_offset=0, ppc_app='searchcommands_app', ppc_user='admin', ppc_bs='$SPLUNK_HOME/etc', bundle_version=0, vix_families=<Element 'root' at 0x103a7e410>, tz='### SERIALIZED TIMEZONE FORMAT 1.0;Y-25200 YW 50 44 54;Y-28800 NW 50 53 54;Y-25200 YW 50 57 54;Y-25200 YG 50 50 54;@-1633269600 0;@-1615129200 1;@-1601820000 0;@-1583679600 1;@-880207200 2;@-769395600 3;@-765385200 1;@-687967200 0;@-662655600 1;@-620834400 0;@-608137200 1;@-589384800 0;@-576082800 1;@-557935200 0;@-544633200 1;@-526485600 0;@-513183600 1;@-495036000 0;@-481734000 1;@-463586400 0;@-450284400 1;@-431532000 0;@-418230000 1;@-400082400 0;@-386780400 1;@-368632800 0;@-355330800 1;@-337183200 0;@-323881200 1;@-305733600 0;@-292431600 1;@-273679200 0;@-260982000 1;@-242229600 0;@-226508400 1;@-210780000 0;@-195058800 1;@-179330400 0;@-163609200 1;@-147880800 0;@-131554800 1;@-116431200 0;@-100105200 1;@-84376800 0;@-68655600 1;@-52927200 0;@-37206000 1;@-21477600 0;@-5756400 1;@9972000 0;@25693200 1;@41421600 0;@57747600 1;@73476000 0;@89197200 1;@104925600 0;@120646800 1;@126698400 0;@152096400 1;@162381600 0;@183546000 1;@199274400 0;@215600400 1;@230724000 0;@247050000 1;@262778400 0;@278499600 1;@294228000 0;@309949200 1;@325677600 0;@341398800 1;@357127200 0;@372848400 1;@388576800 0;@404902800 1;@420026400 0;@436352400 1;@452080800 0;@467802000 1;@483530400 0;@499251600 1;@514980000 0;@530701200 1;@544615200 0;@562150800 1;@576064800 0;@594205200 1;@607514400 0;@625654800 1;@638964000 0;@657104400 1;@671018400 0;@688554000 1;@702468000 0;@720003600 1;@733917600 0;@752058000 1;@765367200 0;@783507600 1;@796816800 0;@814957200 1;@828871200 0;@846406800 1;@860320800 0;@877856400 1;@891770400 0;@909306000 1;@923220000 0;@941360400 1;@954669600 0;@972810000 1;@986119200 0;@1004259600 1;@1018173600 0;@1035709200 1;@1049623200 0;@1067158800 1;@1081072800 0;@1099213200 1;@1112522400 0;@1130662800 1;@1143972000 0;@1162112400 1;@1173607200 0;@1194166800 1;@1205056800 0;@1225616400 1;@1236506400 0;@1257066000 1;@1268560800 0;@1289120400 1;@1300010400 0;@1320570000 1;@1331460000 0;@1352019600 1;@1362909600 0;@1383469200 1;@1394359200 0;@1414918800 1;@1425808800 0;@1446368400 1;@1457863200 0;@1478422800 1;@1489312800 0;@1509872400 1;@1520762400 0;@1541322000 1;@1552212000 0;@1572771600 1;@1583661600 0;@1604221200 1;@1615716000 0;@1636275600 1;@1647165600 0;@1667725200 1;@1678615200 0;@1699174800 1;@1710064800 0;@1730624400 1;@1741514400 0;@1762074000 1;@1772964000 0;@1793523600 1;@1805018400 0;@1825578000 1;@1836468000 0;@1857027600 1;@1867917600 0;@1888477200 1;@1899367200 0;@1919926800 1;@1930816800 0;@1951376400 1;@1962871200 0;@1983430800 1;@1994320800 0;@2014880400 1;@2025770400 0;@2046330000 1;@2057220000 0;@2077779600 1;@2088669600 0;@2109229200 1;@2120119200 0;@2140678800 1;$', msgType=None, msg=None)''' \
            if python_version > 26 else \
            '''SearchResultsInfo(sid=1391366014.3, timestamp=1391366014.7572229, now=1391366014, setStart=1391366007, index_et=1391366011, index_lt=1391366011, startTime=1386621222, rt_earliest=None, rt_latest=None, rtspan=None, scan_count=0, drop_count=0, maxevents=0, countMap={'in_ct.command.fields': 76, 'duration.command.search': 13, 'invocations.startup.handoff': 1, 'duration.dispatch.results_combiner': 1, 'invocations.command.search.kv': 1, 'duration.dispatch.stream.local': 14, 'out_ct.command.head': 10, 'invocations.command.search.rawdata': 1, 'invocations.dispatch.results_combiner': 1, 'invocations.command.fields': 1, 'out_ct.command.search.typer': 76, 'invocations.dispatch.writeStatus': 3, 'invocations.command.search.index': 1, 'duration.command.head': 1, 'duration.dispatch.evaluate': 130, 'duration.dispatch.evaluate.search': 41, 'in_ct.command.search.calcfields': 76, 'duration.dispatch.writeStatus': 3, 'invocations.command.search.tags': 1, 'in_ct.command.search.lookups': 76, 'duration.command.search.tags': 1, 'duration.command.search.lookups': 1, 'invocations.dispatch.evaluate': 1, 'duration.command.fields': 1, 'invocations.command.search.summary': 1, 'duration.dispatch.evaluate.countmatches': 88, 'out_ct.command.prehead': 10, 'in_ct.command.search.typer': 76, 'out_ct.command.search.calcfields': 76, 'invocations.command.head': 1, 'duration.startup.handoff': 39, 'duration.command.search.rawdata': 2, 'duration.command.search.index.usec_1_8': 0, 'invocations.command.search.fieldalias': 1, 'duration.dispatch.createProviderQueue': 27, 'duration.dispatch.fetch': 14, 'out_ct.command.search.tags': 76, 'duration.command.search.typer': 4, 'in_ct.command.head': 10, 'invocations.dispatch.createProviderQueue': 1, 'out_ct.command.fields': 76, 'invocations.dispatch.evaluate.head': 1, 'out_ct.command.search.fieldalias': 76, 'invocations.command.search.typer': 1, 'duration.dispatch.check_disk_usage': 1, 'out_ct.command.search': 76, 'in_ct.command.search': 0, 'invocations.dispatch.fetch': 1, 'duration.command.search.index': 1, 'duration.command.search.summary': 1, 'in_ct.command.search.tags': 76, 'duration.dispatch.evaluate.head': 1, 'duration.command.search.kv': 7, 'invocations.command.search.calcfields': 1, 'duration.command.search.fieldalias': 1, 'invocations.dispatch.evaluate.countmatches': 1, 'in_ct.command.search.fieldalias': 76, 'invocations.command.search': 1, 'invocations.dispatch.stream.local': 1, 'duration.command.search.calcfields': 1, 'invocations.dispatch.check_disk_usage': 1, 'prereport_events': 0, 'invocations.dispatch.evaluate.search': 1, 'invocations.command.search.index.usec_1_8': 7, 'duration.command.prehead': 1, 'invocations.command.prehead': 1, 'invocations.command.search.lookups': 1, 'out_ct.command.search.lookups': 76, 'in_ct.command.prehead': 76}, columnOrder=None, keySet='index::_internal', remoteServers=None, is_remote_sorted=1, rt_backfill=0, read_raw=1, enable_event_stream=1, rtoptions=None, field_rendering=None, query_finished=1, request_finalization=0, auth_token='9ce2897f792c52a6ecdcd2e03aa4677c', splunkd_port=8089, splunkd_protocol='https', splunkd_uri='https://127.0.0.1:8089', internal_only=0, summary_mode='none', summary_maxtimespan=None, summary_stopped=0, is_batch_mode=0, root_sid=None, shp_id='A8797F6F-B6BF-43E9-9AFE-857D2FBC8534', search='search index=_internal | head 10 | countmatches fieldname=word_count pattern=\\\\\\\\w+ uri', remote_search='litsearch index=_internal | fields  keepcolorder=t "*" "_bkt" "_cd" "_si" "host" "index" "linecount" "source" "sourcetype" "splunk_server" "uri,word_count" | prehead  limit=10 null=false keeplast=false', reduce_search=None, datamodel_map=None, tstats_reduce=None, normalized_search='litsearch index=_internal | fields keepcolorder=t "*" "_bkt" "_cd" "_si" "host" "index" "linecount" "source" "sourcetype" "splunk_server" "uri,word_count" | prehead limit=10 null=false keeplast=false', summary_id='A8797F6F-B6BF-43E9-9AFE-857D2FBC8534_searchcommands_app_admin_013dda14f276a384', normalized_summary_id='A8797F6F-B6BF-43E9-9AFE-857D2FBC8534_searchcommands_app_admin_NS91c147524d89ae5a', generation_id=0, label=None, is_saved_search=0, realtime=0, indexed_realtime=0, indexed_realtime_offset=0, ppc_app='searchcommands_app', ppc_user='admin', ppc_bs='$SPLUNK_HOME/etc', bundle_version=0, vix_families=<Element 'root' at 0x103a7e410>, tz='### SERIALIZED TIMEZONE FORMAT 1.0;Y-25200 YW 50 44 54;Y-28800 NW 50 53 54;Y-25200 YW 50 57 54;Y-25200 YG 50 50 54;@-1633269600 0;@-1615129200 1;@-1601820000 0;@-1583679600 1;@-880207200 2;@-769395600 3;@-765385200 1;@-687967200 0;@-662655600 1;@-620834400 0;@-608137200 1;@-589384800 0;@-576082800 1;@-557935200 0;@-544633200 1;@-526485600 0;@-513183600 1;@-495036000 0;@-481734000 1;@-463586400 0;@-450284400 1;@-431532000 0;@-418230000 1;@-400082400 0;@-386780400 1;@-368632800 0;@-355330800 1;@-337183200 0;@-323881200 1;@-305733600 0;@-292431600 1;@-273679200 0;@-260982000 1;@-242229600 0;@-226508400 1;@-210780000 0;@-195058800 1;@-179330400 0;@-163609200 1;@-147880800 0;@-131554800 1;@-116431200 0;@-100105200 1;@-84376800 0;@-68655600 1;@-52927200 0;@-37206000 1;@-21477600 0;@-5756400 1;@9972000 0;@25693200 1;@41421600 0;@57747600 1;@73476000 0;@89197200 1;@104925600 0;@120646800 1;@126698400 0;@152096400 1;@162381600 0;@183546000 1;@199274400 0;@215600400 1;@230724000 0;@247050000 1;@262778400 0;@278499600 1;@294228000 0;@309949200 1;@325677600 0;@341398800 1;@357127200 0;@372848400 1;@388576800 0;@404902800 1;@420026400 0;@436352400 1;@452080800 0;@467802000 1;@483530400 0;@499251600 1;@514980000 0;@530701200 1;@544615200 0;@562150800 1;@576064800 0;@594205200 1;@607514400 0;@625654800 1;@638964000 0;@657104400 1;@671018400 0;@688554000 1;@702468000 0;@720003600 1;@733917600 0;@752058000 1;@765367200 0;@783507600 1;@796816800 0;@814957200 1;@828871200 0;@846406800 1;@860320800 0;@877856400 1;@891770400 0;@909306000 1;@923220000 0;@941360400 1;@954669600 0;@972810000 1;@986119200 0;@1004259600 1;@1018173600 0;@1035709200 1;@1049623200 0;@1067158800 1;@1081072800 0;@1099213200 1;@1112522400 0;@1130662800 1;@1143972000 0;@1162112400 1;@1173607200 0;@1194166800 1;@1205056800 0;@1225616400 1;@1236506400 0;@1257066000 1;@1268560800 0;@1289120400 1;@1300010400 0;@1320570000 1;@1331460000 0;@1352019600 1;@1362909600 0;@1383469200 1;@1394359200 0;@1414918800 1;@1425808800 0;@1446368400 1;@1457863200 0;@1478422800 1;@1489312800 0;@1509872400 1;@1520762400 0;@1541322000 1;@1552212000 0;@1572771600 1;@1583661600 0;@1604221200 1;@1615716000 0;@1636275600 1;@1647165600 0;@1667725200 1;@1678615200 0;@1699174800 1;@1710064800 0;@1730624400 1;@1741514400 0;@1762074000 1;@1772964000 0;@1793523600 1;@1805018400 0;@1825578000 1;@1836468000 0;@1857027600 1;@1867917600 0;@1888477200 1;@1899367200 0;@1919926800 1;@1930816800 0;@1951376400 1;@1962871200 0;@1983430800 1;@1994320800 0;@2014880400 1;@2025770400 0;@2046330000 1;@2057220000 0;@2077779600 1;@2088669600 0;@2109229200 1;@2120119200 0;@2140678800 1;$', msgType=None, msg=None)'''

        command = SearchCommand()
        info_path = os.path.join(TestSearchCommand._package_directory, 'data', 'input', 'externSearchResultsInfo.csv')
        input = StringIO('infoPath:%s\n\nAction\r\naccess_search_results_info' % info_path)
        command.process(args=['foo.py', '__EXECUTE__'], input_file=input, output_file=result)

        observed = re.sub('''vix_families=<Element '?root'? at [^>]+>''', '''vix_families=<Element 'root' at 0x103a7e410>''', repr(command.search_results_info))
        self.assertEqual(expected, observed)

        # Command.process should provide access to a service object when search
        # results info is available

        self.assertIsInstance(command.service, Service)
        self.assertEqual(command.service.authority, command.search_results_info.splunkd_uri)
        self.assertEqual(command.service.scheme, command.search_results_info.splunkd_protocol)
        self.assertEqual(command.service.port, command.search_results_info.splunkd_port)
        self.assertEqual(command.service.token, command.search_results_info.auth_token)
        self.assertEqual(command.service.namespace.app, command.search_results_info.ppc_app)
        self.assertEqual(command.service.namespace.owner, None)
        self.assertEqual(command.service.namespace.sharing, None)

        # Command.process should not provide access to search results info or
        # a service object when the 'infoPath' input header is unavailable

        command = SearchCommand()

        command.process(args=['foo.py', '__EXECUTE__'], input_file=StringIO('\nAction\r\naccess_search_results_info'), output_file=result)
        self.assertEqual(command.search_results_info, None)
        self.assertEqual(command.service, None)

        return

    _package_directory = os.path.dirname(__file__)

if __name__ == "__main__":
    unittest.main()
