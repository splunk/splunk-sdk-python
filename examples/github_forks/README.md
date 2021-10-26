splunk-sdk-python github_forks example
========================================

This app provides an example of a modular input that generates a random number between the min and max values provided by the user during setup of the input.

To run this example locally run `SPLUNK_VERSION=latest docker compose up -d` from the root of this repository which will mount this example alongside the latest version of splunklib within `/opt/splunk/etc/apps/github_forks` and `/opt/splunk/etc/apps/github_forks/lib/splunklib` within the `splunk` container.

Once the docker container is up and healthy log into the Splunk UI and setup a new `Github Repository Forks` input by visiting this page: http://localhost:8000/en-US/manager/github_forks/datainputstats and selecting the "Add new..." button next to the Local Inputs > Random Inputs. Enter values for a Github Repository owner and repo_name, for example owner = `splunk` repo_name = `splunk-sdk-python`.

NOTE: If no Github Repository Forks input appears then the script is likely not running properly, see https://docs.splunk.com/Documentation/SplunkCloud/latest/AdvancedDev/ModInputsDevTools for more details on debugging the modular input using the command line and relevant logs.

Once the input is created you should be able to see an event when running the following search: `source="github_forks://*"` the event should contain fields for `owner` and `repository` matching the values you input during setup and then a `fork_count` field corresponding to the number of forks the repo has according to the Github API.