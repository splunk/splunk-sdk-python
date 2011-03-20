# Export

`export.py` is a sample application to export a portion, or all, events in a 
specific, or all, indices to a CSV file

The CLI arguments for the export are as follows (all arguments are of the form
`arg=value`):

	--index 	specifies the index to export. Default is all indexes.
	--progress 	prints progress to stdout. Default is no progress shown.
	--starttime	starttime in SECONDS from 1970. Default is start at beginning of 
	                index.
	--endtime	endtime in SECONDS from 1970. Default is end at the end of the 
	                index.
	--output	output file name. Default is the current working directory, 
	                export.out.
	--limit		limits the number of events per chunk. The number actually used 
	                may be smaller than this limit. Deafult is 100,000.
	--restart	restarts the export if terminated prematurely.
	--omode		specifies the output format of the resulting export, the 
	                allowable formats are xml, json, csv.

## Possible Future Work

### Friendly start/end times

Currently, the start/end times are given as seconds from 1970, which is not 
the most friendly/intuitive format.

## Notes

* 	The "time chunking" algorithm tries to put as many events, up to the 
	limit specified in a "bucket". We start out by breaking the index into buckets 
	of 86400 seconds, or one day. If the number of events in this bucket is more 
	than our limit, we split the day into 24 buckets of one hour each. If any of the 
	hour buckets contain more events than our limit, the hour is split into 60 
	buckets of one minute each. If any of the minute buckets contain more events 
	than our limit, the minute is split into 60 buckets of one second each. A second
	bucket is the smallest granular size.
	
	The code has a downsample map:
	
	 { 86400 : 3600, 3600 : 60, 60 : 1 }
	
	This maps the current "bucket length in seconds" to "next bucket length in 
	seconds" if the current bucket contains more events than our limit.
	
	As such, it is important that the initial starttime begins on a day boundary 
	(i.e. 12:00:00 AM).

*	The goal of export.py is NOT to optimize the number of requests to splunk, 
	rather to optimize the size of the return request from splunk so that in the 
	cases of very large indices, robustness and restart are paramount.

* 	When using csv or json output formats, sideband messages are not included. If 
	you wish to capture sideband messages, the xml format should be used.