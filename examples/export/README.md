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

* 	When using csv or json output formats, sideband messages are not included. If 
	you wish to capture sideband messages, the xml format should be used.