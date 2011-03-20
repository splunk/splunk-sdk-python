# Leftronic Dashboard Integration Sample

This sample shows how to use the Python SDK and Splunk to integrate with
a third party tool (or service). In this specific case, we use a 
Leftronic Dashboard to show real-time Twitter data that we are indexing
using the `twitted` example in the SDK.

## How It Works

There are two logical components to the sample: getting data from Splunk and
pushing data to Leftronic.

In order to get data from Splunk, we start a variety of real time searches.
For example, we have searches to get the current top hashtags (in a 5 minute
sliding window), where users are tweeting from, etc.

We then start a loop which will ask each search job for new results, and we
then put the results in a form that Leftronic can understand. Once the results
are formed, we send them over to Leftronic using their API.

## How To Run It

You need to change the code file to include your Leftronic access key. Once you
do, you can simply run it by executing:

	./feed.py

You will also need to run the `twitted` sample at the same time.