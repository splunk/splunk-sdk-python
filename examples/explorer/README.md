# Splunk API Explorer

The 'explorer' example is a browser-based API explorer. It is keyed of the same
data that generates the Splunk REST reference docs, and so is meant to be
authoritative.

To run, simply execute:

    ./explorer.py

It will pick up all relevant values from your .splunkrc, or you can pass them 
in on the command line. You can see help by adding `--help` to the exectuion.

The API Explorer will open up a browser window that will show you a drop down
for all the Splunk REST APIs, as well as server configuration information
to know which server to connect to.

Once an API is chosen, a API-specific form will be created that will allow you
to fill in all the parameters required by the specific API. It will also
validate that all required parameters are present. 

When the API call is made, it will issue a call to the Splunk server (through a
locally hosted redirect server to work around cross-domain issues), and display
the response it received.

If you are using a web browser on a different machine than you're running
explorer.py on, you need to open explorer.html by hand, and set the values at
the top of the page appropriately. Scheme, host, and port are the values
required for explorer.py to refer to splunkd. So if explorer.py is running on
the same machine as splunkd, then host can be set to localhost even though from
the browser you are opening explorer.html in, it may not be localhost. The values
of redirect host and redirect port are the host and port your browser needs to refer
to to reach explorer.py. The default port for explorer.py is 8080. You can leave
owner and app empty, but set username and password to your login information for
splunkd.

## Future Work

- Switch to JSONP once the server supports it
- Validate parameter types (int, string, enum, etc)