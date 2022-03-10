splunk-sdk-python github_commits example
========================================

This app provides an example of a modular input that Pulls down commit data from GitHub and creates events for each commit, which are then streamed to Splunk, based on the owner and repo_name provided by the user during setup of the input.

To run this example locally run `SPLUNK_VERSION=latest docker compose up -d` from the root of this repository which will mount this example alongside the latest version of splunklib within `/opt/splunk/etc/apps/github_commits` and `/opt/splunk/etc/apps/github_commits/lib/splunklib` within the `splunk` container.

Once the docker container is up and healthy log into the Splunk UI and setup a new `Github Commits` input by visiting this page: http://localhost:8000/en-US/manager/github_commits/datainputstats and selecting the "Add new..." button next to the Local Inputs > Github Commits. Enter values for a Github Repository owner and repo_name, for example owner = `splunk` repo_name = `splunk-sdk-python`.
(optional) `token` if using a private repository and/or to avoid Github's API limits. To get a Github API token visit the [Github settings page](https://github.com/settings/tokens/new) and make sure the repo and public_repo scopes are selected.

NOTE: If no events appears then the script is likely not running properly, see https://docs.splunk.com/Documentation/SplunkCloud/latest/AdvancedDev/ModInputsDevTools for more details on debugging the modular input using the command line and relevant logs.

Once the input is created you should be able to see an event when running the following search: `source="github_commits://*"` the event should contain commit data from given GitHub repository.
