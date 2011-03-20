# Saved Search

The saved search example supports `create`, `list`, `list-all` and `delete` 
saved search actions.

`list-all` requires no argument, and will display all saved searches.

`list` and `delete` requires the `--name` argument to either list the contents 
of a specific saved search or delete a specific saved search.

`create` requires the `--name` argument, as well as a littany of other arguments 
to establish a saved search. The help output is seen below.

Of special note is the events that can perform actions (`--actions` and 
`--action.<action_type>.<custome_key>=...`). Email, rss and scripts can be 
invoked as a result of the event firing. Scripts are run out of 
`$SPLUNK_HOME/bin/scripts/`.

```
Options:
  -h, --help            show this help message and exit
  --is_visible=IS_VISIBLE
                        <optional for create> Should the saved search appear
                        under the Seaches & Report menu (defaults to true)
  --alert_type=ALERT_TYPE
                        <optional for create> The thing to count a quantity of
                        in relation to relation. Required for Alerts. (huh?)
  --dispatch.max_count=DISPATCH.MAX_COUNT
                        <optional for create> Maximum number of results
  --action.<action_type>.<custom_key>=ACTION.<ACTION_TYPE>.<CUSTOM_KEY>.
                        <optional for create> A key/value pair that is
                        specific to the action_type. For example, if actions
                        contains email, then the following keys would be
                        necessary: action.email.to=foo@splunk.com  and
                        action.email.sender=splunkbot. For scripts:
                        action.script.filename=doodle.py (note: script is run
                        from $SPLUNK_HOME/bin/scripts/)
  --actions=ACTIONS     <optional for create> A list of the actions to fire on
                        alert; supported values are {(email, rss) | script}.
                        For example, actions = rss,email would enable both RSS
                        feed and email sending. Or if you want to just fire a
                        script: actions = script
  --dispatch.earliest_time=DISPATCH.EARLIEST_TIME
                        <optional for create> The earliest time for the search
  --is_scheduled=IS_SCHEDULED
                        <optional for create> Does the saved search run on the
                        saved schedule.
  --dispatch.lookups=DISPATCH.LOOKUPS
                        <optional for create> Boolean flag indicating whether
                        to enable lookups in this search
  --operation=OPERATION
                        <optional for create> type of splunk operation: list-
                        all, list, create, delete (defaults to list-all)
  --port=PORT           Port number (default 8089)
  --alert_threshold=ALERT_THRESHOLD
                        <optional for create> The quantity of counttype must
                        exceed in relation to relation. Required for Alerts.
                        (huh?)
  --dispatch.latest_time=DISPATCH.LATEST_TIME
                        <optional for create> The latest time for the search
  --alert.supress_keys=ALERT.SUPRESS_KEYS
                        <optional for create> [string] comma delimited list of
                        keys to use for suppress, to access result values use
                        result.<field-name> syntax
  --namespace=NAMESPACE
  --scheme=SCHEME       Scheme (default 'https')
  --config=CONFIG       Load options from config file
  --dispatch.spawn_process=DISPATCH.SPAWN_PROCESS
                        <optional for create> Boolean flag whether to spawn
                        the search as a separate process
  --alert.supress.period=ALERT.SUPRESS.PERIOD
                        <optional for create> [time-specifier] suppression
                        period, use ack to suppress until acknowledgment is
                        received
  --username=USERNAME   Username to login with
  --alert.digest=ALERT.DIGEST
                        <optional for create> [bool] whether the alert actions
                        are executed on the entire result set or on each
                        individual result (defaults to true)
  --cron_schedule=CRON_SCHEDULE
                        <optional for create> The cron formatted schedule of
                        the saved search. Required for Alerts
  --alert_comparator=ALERT_COMPARATOR
                        <optional for create> The relation the count type has
                        to the quantity. Required for Alerts. (huh?)
  --run_on_startup=RUN_ON_STARTUP
                        <optional for create> Should the scheduler run this
                        saved search on splunkd start up (defaults to false)
  --realtime_schedule=REALTIME_SCHEDULE
                        <optional for create> Is the scheduler allowed to skip
                        executions of this saved search, if there is not
                        enough search bandwidtch (defaults to true), set to
                        false only for summary index populating searches
  --alert.expires=ALERT.EXPIRES
                        <optional for create> [time-specifier] The period of
                        time for which the alert will be shown in the alert's
                        dashboard
  --host=HOST           Host name (default 'localhost')
  --dispatch.max_time=DISPATCH.MAX_TIME
                        <optional for create> Maximum amount of time in
                        seconds before finalizing the search
  --output_mode=OUTPUT_MODE
                        <optional for all> type of output (atom, xml)
  --dispatch.buckets=DISPATCH.BUCKETS
                        <optional for create> The number of event buckets
                        (huh?)
  --password=PASSWORD   Password to login with
  --max_concurrent=MAX_CONCURRENT
                        <optional for create> If the search is ran by the
                        scheduler how many concurrent instances of this search
                        is the scheduler allowed to run (defaults to 1)
  --search=SEARCH       <required for create> splunk search string
  --dispatch.time_format=DISPATCH.TIME_FORMAT
                        <optional for create> Format string for
                        earliest/latest times
  --name=NAME           <required for all> name of search name to be created
  --alert.severity=ALERT.SEVERITY
                        <optional for create> [int] Specifies the alert
                        severity level, valid values are: 1-debug, 2-info,
                        3-warn, 4-error, 5-severe, 6-fatal
  --alert.supress=ALERT.SUPRESS
                        <optional for create> [bool]whether alert suppression
                        is enabled for this scheduled search
  --dispatch.ttl=DISPATCH.TTL
                        <optional for create> The TTL of the search job
                        created
```
