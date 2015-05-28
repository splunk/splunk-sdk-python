#!/usr/bin/env python
#
# Copyright 2013 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys, urllib2, json

from splunklib.modularinput import *

class MyScript(Script):
    """All modular inputs should inherit from the abstract base class Script
    from splunklib.modularinput.script.
    They must override the get_scheme and stream_events functions, and,
    if the scheme returned by get_scheme has Scheme.use_external_validation
    set to True, the validate_input function.
    """
    def get_scheme(self):
        """When Splunk starts, it looks for all the modular inputs defined by
        its configuration, and tries to run them with the argument --scheme.
        Splunkd expects the modular inputs to print a description of the
        input in XML on stdout. The modular input framework takes care of all
        the details of formatting XML and printing it. The user need only
        override get_scheme and return a new Scheme object.

        :return: scheme, a Scheme object
        """
        # Splunk will display "Github Repository Forks" to users for this input
        scheme = Scheme("Github Repository Forks")

        scheme.description = "Streams events giving the number of forks of a GitHub repository."
        # If you set external validation to True, without overriding validate_input,
        # the script will accept anything as valid. Generally you only need external
        # validation if there are relationships you must maintain among the
        # parameters, such as requiring min to be less than max in this example,
        # or you need to check that some resource is reachable or valid.
        # Otherwise, Splunk lets you specify a validation string for each argument
        # and will run validation internally using that string.
        scheme.use_external_validation = True
        scheme.use_single_instance = True

        owner_argument = Argument("owner")
        owner_argument.title = "Owner"
        owner_argument.data_type = Argument.data_type_string
        owner_argument.description = "Github user or organization that created the repository."
        owner_argument.required_on_create = True
        # If you are not using external validation, you would add something like:
        #
        # scheme.validation = "owner==splunk"
        scheme.add_argument(owner_argument)

        repo_name_argument = Argument("repo_name")
        repo_name_argument.title = "Repo Name"
        repo_name_argument.data_type = Argument.data_type_string
        repo_name_argument.description = "Name of the Github repository."
        repo_name_argument.required_on_create = True
        scheme.add_argument(repo_name_argument)

        return scheme

    def validate_input(self, validation_definition):
        """In this example we are using external validation to verify that the Github
        repository exists. If validate_input does not raise an Exception, the input
        is assumed to be valid. Otherwise it prints the exception as an error message
        when telling splunkd that the configuration is invalid.

        When using external validation, after splunkd calls the modular input with
        --scheme to get a scheme, it calls it again with --validate-arguments for
        each instance of the modular input in its configuration files, feeding XML
        on stdin to the modular input to do validation. It is called the same way
        whenever a modular input's configuration is edited.

        :param validation_definition: a ValidationDefinition object
        """
        # Get the values of the parameters, and construct a URL for the Github API
        owner = validation_definition.parameters["owner"]
        repo_name = validation_definition.parameters["repo_name"]
        repo_url = "https://api.github.com/repos/%s/%s" % (owner, repo_name)

        # Read the response from the Github API, then parse the JSON data into an object
        response = urllib2.urlopen(repo_url).read()
        jsondata = json.loads(response)

        # If there is only 1 field in the jsondata object,some kind or error occurred
        # with the Github API.
        # Typically, this will happen with an invalid repository.
        if len(jsondata) == 1:
            raise ValueError("The Github repository was not found.")

        # If the API response seems normal, validate the fork count
        # If there's something wrong with getting fork_count, raise a ValueError
        try:
            fork_count = int(jsondata["forks_count"])
        except ValueError as ve:
            raise ValueError("Invalid fork count: %s", ve.message)

    def stream_events(self, inputs, ew):
        """This function handles all the action: splunk calls this modular input
        without arguments, streams XML describing the inputs to stdin, and waits
        for XML on stdout describing events.

        If you set use_single_instance to True on the scheme in get_scheme, it
        will pass all the instances of this input to a single instance of this
        script.

        :param inputs: an InputDefinition object
        :param ew: an EventWriter object
        """
        # Go through each input for this modular input
        for input_name, input_item in inputs.inputs.iteritems():
            # Get fields from the InputDefinition object
            owner = input_item["owner"]
            repo_name = input_item["repo_name"]

            # Get the fork count from the Github API
            repo_url = "https://api.github.com/repos/%s/%s" % (owner, repo_name)
            response = urllib2.urlopen(repo_url).read()
            jsondata = json.loads(response)
            fork_count = jsondata["forks_count"]

            # Create an Event object, and set its fields
            event = Event()
            event.stanza = input_name
            event.data = 'owner="%s" repository="%s" fork_count=%s' % \
                         (owner.replace('"', '\\"'), repo_name.replace('"', '\\"'), fork_count)

            # Tell the EventWriter to write this event
            ew.write_event(event)

if __name__ == "__main__":
    sys.exit(MyScript().run(sys.argv))