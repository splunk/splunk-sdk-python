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

from __future__ import absolute_import

import os
import re
import sys
import json
# NOTE: splunklib must exist within github_commits/lib/splunklib for this
# example to run! To run this locally use `SPLUNK_VERSION=latest docker compose up -d`
# from the root of this repo which mounts this example and the latest splunklib
# code together at /opt/splunk/etc/apps/github_commits
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from splunklib.modularinput import *
from splunklib import six
from six.moves import http_client


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
        # Splunk will display "Github Commits" to users for this input
        scheme = Scheme("Github Commits")

        scheme.description = "Streams events of commits in the specified Github repository (must be public, unless setting a token)."
        # If you set external validation to True, without overriding validate_input,
        # the script will accept anything as valid. Generally you only need external
        # validation if there are relationships you must maintain among the
        # parameters, such as requiring min to be less than max in this example,
        # or you need to check that some resource is reachable or valid.
        # Otherwise, Splunk lets you specify a validation string for each argument
        # and will run validation internally using that string.
        scheme.use_external_validation = True
        scheme.use_single_instance = False  # Set to false so an input can have an optional interval parameter.

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

        token_argument = Argument("token")
        token_argument.title = "Token"
        token_argument.data_type = Argument.data_type_string
        token_argument.description = "(Optional) A Github API access token. Required for private repositories (the token must have the 'repo' and 'public_repo' scopes enabled). Recommended to avoid Github's API limit, especially if setting an interval."
        token_argument.required_on_create = False
        token_argument.required_on_edit = False
        scheme.add_argument(token_argument)

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
        token = None
        if "token" in validation_definition.parameters:
            token = validation_definition.parameters["token"]

        # Call Github to retrieve repo information
        res = _get_github_commits(owner, repo_name, 1, 1, token)

        # If we get any kind of message, that's a bad sign.
        if "message" in res:
            raise ValueError("Some error occur during fetching commits. - " + res["message"])
        elif len(res) == 1 and "sha" in res[0]:
            pass
        else:
            raise ValueError("Expected only the latest commit, instead found " + str(len(res)) + " commits.")

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
        for input_name, input_item in six.iteritems(inputs.inputs):
            # Get fields from the InputDefinition object
            owner = input_item["owner"]
            repo_name = input_item["repo_name"]
            token = None
            if "token" in input_item:
                token = input_item["token"]
            # Get the checkpoint directory out of the modular input's metadata
            checkpoint_dir = inputs.metadata["checkpoint_dir"]

            checkpoint_file_path = os.path.join(checkpoint_dir, owner + " " + repo_name + ".txt")
            checkpoint_file_new_contents = ""
            error_found = False

            # Set the temporary contents of the checkpoint file to an empty string
            checkpoint_file_contents = ""

            try:
                # read sha values from file, if exist
                file = open(checkpoint_file_path, 'r')
                checkpoint_file_contents = file.read()
                file.close()
            except:
                # If there's an exception, assume the file doesn't exist
                # Create the checkpoint file with an empty string
                file = open(checkpoint_file_path, "a")
                file.write("")
                file.close()

            per_page = 100  # The maximum per page value supported by the Github API.
            page = 1

            while True:
                # Get the commit count from the Github API
                res = _get_github_commits(owner, repo_name, per_page, page, token)
                if len(res) == 0:
                    break

                file = open(checkpoint_file_path, "a")

                for record in res:
                    if error_found:
                        break

                    # If the file exists and doesn't contain the sha, or if the file doesn't exist.
                    if checkpoint_file_contents.find(record["sha"] + "\n") < 0:
                        try:
                            _stream_commit(ew, owner, repo_name, record)
                            # Append this commit to the string we'll write at the end
                            checkpoint_file_new_contents += record["sha"] + "\n"
                        except:
                            error_found = True
                            file.write(checkpoint_file_new_contents)

                            # We had an error, die.
                            return

                file.write(checkpoint_file_new_contents)
                file.close()

                page += 1


def _get_display_date(date):
    month_strings = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    date_format = "%Y-%m-%d %H:%M:%S"
    date = datetime.strptime(date, date_format)

    hours = date.hour
    if hours < 10:
        hours = "0" + str(hours)

    mins = date.minute
    if mins < 10:
        mins = "0" + str(mins)

    return "{month} {day}, {year} - {hour}:{minute} {period}".format(month=month_strings[date.month - 1], day=date.day,
                                                                     year=date.year, hour=hours, minute=mins,
                                                                     period="AM" if date.hour < 12 else "PM")


def _get_github_commits(owner, repo_name, per_page=1, page=1, token=None):
    # Read the response from the Github API, then parse the JSON data into an object
    repo_path = "/repos/%s/%s/commits?per_page=%d&page=%d" % (owner, repo_name, per_page, page)
    connection = http_client.HTTPSConnection('api.github.com')
    headers = {
        'Content-type': 'application/json',
        'User-Agent': 'splunk-sdk-python'
    }
    if token:
        headers['Authorization'] = 'token ' + token
    connection.request('GET', repo_path, headers=headers)
    response = connection.getresponse()
    body = response.read().decode()
    return json.loads(body)


def _stream_commit(ew, owner, repo_name, commitData):
    json_data = {
        "sha": commitData["sha"],
        "api_url": commitData["url"],
        "url": "https://github.com/" + owner + "/" + repo_name + "/commit/" + commitData["sha"]
    }
    commit = commitData["commit"]

    # At this point, assumed checkpoint doesn't exist.
    json_data["message"] = re.sub("\n|\r", " ", commit["message"])
    json_data["author"] = commit["author"]["name"]
    json_data["rawdate"] = commit["author"]["date"]
    commit_date = re.sub("T|Z", " ", commit["author"]["date"]).strip()
    json_data["displaydate"] = _get_display_date(commit_date)

    # Create an Event object, and set its fields
    event = Event()
    event.stanza = repo_name
    event.sourceType = "github_commits"
    event.data = json.dumps(json_data)

    # Tell the EventWriter to write this event
    ew.write_event(event)


if __name__ == "__main__":
    sys.exit(MyScript().run(sys.argv))
