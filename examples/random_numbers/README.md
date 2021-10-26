splunk-sdk-python random_numbers example
========================================

This app provides an example of a modular input that generates a random number between the min and max values provided by the user during setup of the input.

To run this example locally run `SPLUNK_VERSION=latest docker compose up -d` from the root of this repository which will mount this example alongside the latest version of splunklib within `/opt/splunk/etc/apps/random_numbers` and `/opt/splunk/etc/apps/random_numbers/lib/splunklib` within the `splunk` container.

Once the docker container is up and healthy log into the Splunk UI and setup a new `Random Numbers` input by visiting this page: http://localhost:8000/en-US/manager/random_numbers/datainputstats and selecting the "Add new..." button next to the Local Inputs > Random Inputs. If no Random Numbers input appears then the script is likely not running properly, see https://docs.splunk.com/Documentation/SplunkCloud/latest/AdvancedDev/ModInputsDevTools for more details on debugging the modular input using the command line and relevant logs.