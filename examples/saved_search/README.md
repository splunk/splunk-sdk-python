# Saved Search

The saved search example supports `create`, `list`, `list-all` and `delete` 
saved search actions.

`list-all` requires no argument, and will display all saved searches.

`list` and `delete` requires the `--name` argument to either list the contents 
of a specific saved search or delete a specific saved search.

`create` requires the `--name` argument, as well as a list of any other arguments 
to establish a saved search. The help output is seen below.

Of special note is the events that can perform actions (`--actions` and 
`--action.<action_type>.<custome_key>=...`). Email, rss and scripts can be 
invoked as a result of the event firing. Scripts are run out of 
`$SPLUNK_HOME/bin/scripts/`.

