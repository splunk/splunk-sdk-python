# Custom Search

custom_search is a custom Splunk app (http://www.splunk.com/base/Documentation/latest/Developer/AppIntro) 
that provides a single custom search command 'usercount'.

The purpose of the app is to provide an example of how to define a custom search 
command, how to configure it, and what the input and output should look like in 
order to work with Splunk. Most of this is also documented in the Splunk 
documentation at http://www.splunk.com/base/Documentation/latest/SearchReference/Aboutcustomsearchcommands

## Example Commands

*   Count the number of processes each user has in a unix "top" event: 
    [examples/custom_search/bin/usercount.py](https://github.com/splunk/splunk-sdk-python/blob/master/examples/custom_search/bin/usercount.py)
*   Count the top hashtags in a set of tweets:
    [examples/twitted/twitted/bin/tophashtags.py](https://github.com/splunk/splunk-sdk-python/blob/master/examples/twitted/twitted/bin/tophashtags.py)
*   Add a hashtags multivalue field to each tweet:
    [examples/twitted/twitted/bin/hashtags.py](https://github.com/splunk/splunk-sdk-python/blob/master/examples/twitted/twitted/bin/hashtags.py)

## Defining a Custom Search Command

A custom search command is merely a Python script that reads input from stdin 
and writes output to stdout. Input comes in as CSV (with an optional header), 
and is in general meant to be read using Python's stdlib csv module 
(using `csv.reader` or `csv.DictReader`). Output is also expected to be in CSV, 
and is likewise meant to be used with `csv.writer` or `csv.DictWriter`.

## Conceptual

As noted above, a custom search command is just a Python script that reads data 
in and writes data out. However, it might be useful to make a distinction 
between two subtypes of custom search commands:

*   A streaming custom search command is one that is streamed data in. You can 
    think of it as applying a "function"/"transformation" to each event and then 
    writing out the result of that operation. It is a kind of "mapper". An 
    example of such a command might be a command that adds a field to each event.
*   A non-streaming custom search command expects to have all the data before 
    it operates on it. As such, it is usually "reducing" the data into the 
    output by applying some sort of summary transformation on it. An example of 
    a non-streaming command is the 'stats' command, which will collect all the 
    data before it can calculate the statistics.

Note that neither of these cases precludes having previews of the data, and you 
can enable or disable preview functionality in the configuration.

## Configuration

Configuration of custom search commands is done in the local/commands.conf file 
of your custom app. You can take a look at a few examples in the SDK:

*   [examples/custom_search/local/commands.conf](https://github.com/splunk/splunk-sdk-python/blob/master/examples/custom_search/local/commands.conf)
*   [examples/twitted/twitted/local/commands.conf](https://github.com/splunk/splunk-sdk-python/blob/master/examples/twitted/twitted/local/commands.conf)

The authoritative documentation for commands.conf can be found here: 
http://www.splunk.com/base/Documentation/latest/Admin/commandsconf

## Input

The input format is just CSV, with an optional header. The general format 
definition is:

a.  Several lines of header, in the form of "key:value" pairs, separated by 
    new lines. OPTIONAL
b.  A blank newline
c.  Data

The presence of the header (and some fields in it) can be controlled in 
commands.conf.

Included an annotated sample input below. Python style '###' comments are used 
to point out salient features. This input is truncated for brevity - you can see 
the full input at tests/custom_search/usercount.in

```
### The following line is the first line of the header
authString:<auth><userId>itay</userId><username>itay</username><authToken>6e49d9164a4eced1a006f46d5710715c</authToken></auth>
sessionKey:6e49d9164a4eced1a006f46d5710715c
owner:itay
namespace:custom_search
keywords:%22%22%22sourcetype%3A%3Atop%22%22%20%22
search:search%20sourcetype%3D%22top%22%20%7C%20head%202%20%7C%20usercount%20%7C%20head%20100%20%7C%20export
sid:1310074215.71
realtime:0
preview:0
truncated:0
### The above line is the last line of the header, following by the mandatory blank line.

### Data starts in the line below. The first line includes the CSV "column headers", followed by the actual data for each row
"_cd","_indextime","_kv","_raw","_serial","_si","_sourcetype","_time",eventtype,host,index,linecount,punct,source,sourcetype,"splunk_server","tag::eventtype",timestamp
"28:138489",1310074203,1,"   PID  USER              PR    NI    VIRT     RES     SHR   S  pctCPU  pctMEM       cpuTIME  COMMAND
   469  root               ?     ?   2378M   1568K    244K   ?     7.2       ?      00:00.15  top
    95  _coreaudiod        ?     ?   2462M     12M    952K   ?     5.3       ?      88:47.70  coreaudiod
  7722  itay               ?     ?   4506M    608M     99M   ?     3.9       ?      75:02.81  pycharm
",0,"Octavian.local
os",top,1310074203,"top usb_device_registration_Linux_syslog","Octavian.local",os,120,"__________________________________________________",top,top,"Octavian.local","Linux
USB
device
os
process
registration
report
success
syslog
top",none
### This is the start of the second CSV record
"28:138067",1310074173,1,"   PID  USER              PR    NI    VIRT     RES     SHR   S  pctCPU  pctMEM       cpuTIME  COMMAND
   369  root               ?     ?   2378M   1568K    244K   ?     7.3       ?      00:00.15  top
    95  _coreaudiod        ?     ?   2462M     12M    952K   ?     5.4       ?      88:46.09  coreaudiod
  7722  itay               ?     ?   4506M    608M     99M   ?     3.9       ?      75:01.67  pycharm
",1,"Octavian.local
os",top,1310074173,"top usb_device_registration_Linux_syslog","Octavian.local",os,120,"__________________________________________________",top,top,"Octavian.local","Linux
USB
device
os
process
registration
report
success
syslog
top",none
### Above line is end of input
```

## Output

Output of a custom search command is also in CSV. It follows the same format as 
the input: an optional header, followed by a blank line, followed by the data. 
Included below is a sample output for the above input:

```
### The configuration does not call for a header, so we start with the data immediately. The below line are the CSV column headers.
daemon,usbmuxd,windowserver,www,mdnsresponder,coreaudiod,itay,locationd,root,spotlight
1,1,1,1,1,1,73,1,37,1
1,1,1,1,1,1,73,1,37,1
### The end of the output. The preceding lines are the actual records for each row
```