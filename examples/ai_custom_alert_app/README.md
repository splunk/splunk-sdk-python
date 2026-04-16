
# Threat Level Assessment

A minimal Splunk App that provides a custom alert action for AI-powered severity assessment.
It includes a simple log server for sending events to Splunk, and a saved search which triggers the custom alert when suspicious activity is detected.

## Setup

1. In `./bin/log_server.py` update credentials to ensure the server can connect to your Splunk instance and run the script either in or outside your Splunk environment.
2. In `./default/savedsearches.conf` set `enableSched = 1` to enable the saved search to run every minute.
3. Wait for the saved search to run and see if the `threat_level_assessment` custom alert has been triggered
   `index="main" sourcetype="ai_custom_alert_app:threat_log"`
4. Search `index="main" sourcetype="ai_custom_alert_app:assessment"` to verify results of the AI severity assessment

## Troubleshooting

- Look for all events sent from this app

```spl
`index="main" sourcetype="ai_custom_alert_app:*"`
```

- Look in splunkd logs

```spl
index="_internal" source="/opt/splunk/var/log/splunk/splunkd.log" ai_custom_alert_app
```
