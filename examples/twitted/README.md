# Twitted 

This is a simple Splunk application that indexes the output of the Twitter
"spritzer" and provides a collection of saved searches for inspecting the
resulting Twitter data, and also two sample custom search commands.

This sample serves two purposes: first, it's a fun and readily available data
source to use to learn and explore Splunk, and second, the input script
demonstrates how to use the SDK to "push" data into Splunk using a TCP input.

Note that the input script is not implemented as a Splunk scripted input. It's
designed to run standalone so that it's convenient for you to experiment with.
If this were a real Splunk app, the input Script would be written as a full
Splunk scripted input so that Splunk could manage its execution.

In order to deploy the application, all you need to do is copy (or link) the
twitted sub directory (aka, .../splunk-sdk-python/examples/twitted/twitted) to
the Splunk app directory at $SPLUNK_HOME/etc/apps/twitted.

Then, to run the app all you have to do is type:

    python ./input.py

and the script will prompt you for your Twitter credentials. The script takes a
--verbose={0..2} flag so that you can specify how much info is written to
stdout. Note that the verbosity level does not change what the script feeds
to Splunk for indexing.

Once the input script is up and running, you can start exploring the data using
Splunk or the splunk CLI or any of the SDK command line tools.

