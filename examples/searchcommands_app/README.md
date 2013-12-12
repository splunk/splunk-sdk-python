splunk-sdk-python search_commands_app example
=============================================

This app provides three examples of custom search commands; one of each of the
base types:

 Command      | Type       | Description
:------------ |:-----------|:----------------------------------------------------
 simulate     | Generating | Generates a sequence of events drawn from a csv file using repeated random sampling with replacement
 sum          | Reporting  | Adds all the numbers in a set of fields.
 countmatches | Streaming  | Counts the number of non-overlapping matches to a regular expression in a set of fields.

The app is tested on Splunk 5 and 6. Here is its manifest:

```
├── bin
│   ├── splunklib
│   │   └── searchcommands ....... splunklib.searchcommands module
│   ├── simulate.py .............. SimulateCommand implementation
│   ├── sum.py ................... SumCommand implementation
│   └── countmatches.py .......... CountMatchesCommand implementation
└── default
   ├── data
   │   └── ui
   │       └── nav
   │           └── default.xml ..
   ├── app.conf ................. Used by Splunk to maintain app state [1]
   ├── commands.conf ............ Search command configuration [2]
   ├── logging.conf ............. Python logging[3] configuration in ConfigParser[4] format
   └── logging.debug.conf ....... Logs to app root directory as well as the Splunk log file
```
**References**  
[1] [app.conf](http://docs.splunk.com/Documentation/Splunk/6.0.1/Admin/Appconf app.conf)  
[2] [commands.conf](http://docs.splunk.com/Documentation/Splunk/6.0.1/Admin/Commandsconf)  
[3] [Python Logging HOWTO](http://docs.python.org/2/howto/logging.html)  
[4] [ConfigParser—Configuration file parser](http://docs.python.org/2/library/configparser.html)

## Installation

+ Install the app by copying the `searchcommands_app` directory to
  `$SPLUNK_HOME/etc/apps/searchcommands_app`.

+ Recursively copy `splunklib/searchcommands/*` to
  `$SPLUNK_HOME/etc/apps/searchcommands_app/splunklib/searchcommands`

+ (Re)start Splunk so that the app is recognized.

## Dashboards and Searches

+ TODO: Add saved search(es) for each example

### Searches

+ TODO: Describe saved searches

## License

This software is licensed under the Apache License 2.0. Details can be found in
the file LICENSE.
