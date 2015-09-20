splunk-sdk-python searchcommands_app example
=============================================

This app provides several examples of custom search commands which illustrate each of the base types:

 Command          | Type       | Description
:---------------- |:-----------|:-------------------------------------------------------------------------------------------
 countmatches     | Streaming  | Counts the number of non-overlapping matches to a regular expression in a set of fields.
 generatetext     | Generating | Generates a specified number of events containing a specified text string.
 pypygeneratetext |            | Executes generatetext with PyPy 
 simulate         | Generating | Generates a sequence of events drawn from a csv file using repeated random sampling with replacement
 sum              | Reporting  | Adds all the numbers in a set of fields.
 
The app is tested on Splunk 5 and 6. Here is its manifest:

```
├── bin
│   ├── splunklib
│   │   └── searchcommands ....... splunklib.searchcommands module
│   ├── countmatches.py .......... CountMatchesCommand implementation
│   ├── generatetext.py .......... GenerateTextCommand implementation
│   ├── pypygeneratetext.py ...... Executes generatetext.py with PyPy
│   ├── simulate.py .............. SimulateCommand implementation
│   ├── sum.py ................... SumCommand implementation
│   └── 
├── default
│   ├── data
│   │   └── ui
│   │       └── nav
│   │           └── default.xml ..
│   ├── app.conf ................. Used by Splunk to maintain app state [1]
│   ├── commands.conf ............ Search command configuration [2]
│   ├── logging.conf ............. Python logging[3] configuration in ConfigParser[4] format
│   └── searchbnf.conf ........... Search assistant configuration [5]
└── metadata
    └── local.meta ............... Permits the search assistant to use searchbnf.conf[6]
```
**References**  
[1] [app.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Appconf app.conf)  
[2] [commands.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Commandsconf)  
[3] [Python Logging HOWTO](http://docs.python.org/2/howto/logging.html)  
[4] [ConfigParser—Configuration file parser](http://docs.python.org/2/library/configparser.html)
[5] [searchbnf.conf](http://docs.splunk.com/Documentation/Splunk/latest/admin/Searchbnfconf)
[6] [Set permissions in the file system](http://goo.gl/1oDT7r)

## Installation

+ Link the app to $SPLUNK_HOME/etc/apps/searchcommands_app by running this command:

  ```
  ./setup.py link --scp-version {1|2}
  ```
  
+ Or build a tarball to install on any Splunk instance by running this command:

  ```
  ./setup.py build --scp-version {1|2}
  ```

  The tarball is build as build/searchcommands_app-1.5.0-private.tar.gz.
  
+ And then (re)start Splunk so that the app is recognized.

## Dashboards and Searches

+ TODO: Add saved search(es) for each example

### Searches

+ TODO: Describe saved searches

## License

This software is licensed under the Apache License 2.0. Details can be found in
the file LICENSE.
