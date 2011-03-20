# Excel OData Example

## How To Use

In order to use the `excel_proxy= shim to connect to Microsoft Office's Excel + 
Powerpivot, you need to follow the following instructions:

1. 	Office 2010 is required. Dowload the free powerpivot plugin for excel from 
	http://www.powerpivot.com
2. 	Install and run splunkd on whatever platform you see fit. 
3. 	Using the splunkweb tool, set up splunk to index whatever it is you wish 
	to index.
4. 	Using the splunkweb tool, create custom saved searches.
5. 	On the machine where the splunk python SDK is installed, create or modify 
	`~/.splunkrc` to set the credentials to access the splunkd server. 
	For example:
	
	```
	host=127.0.0.1
	user=admin
	password=changed
	```

6. 	run the excel_proxy.py -- you should see something like:

	```
	splunk proxy: connect to http://192.168.242.179:8086/...
	```

7. 	From Excel, launch the powerpivot window.
8. 	From the powerpivot window, select "From data feed" which will launch a 
	dialog.
9. 	For the URL, use the dns name or IP address of the machine running the 
	shim. For example:

	http://192.168.242.179:8086/Catalog/

10. This should initiate a connection to the shim, that connects to splunkd 
	to return a catalog of all saved searches
11. In powerpivot you can select one or more saved searches to pull into 
	powerpivot
12. You also have an opportunity to exclude certain columns from the final 
	import.
13. When you click finish, the selected searches (and columns) will import 
	the raw splunk event data into powerpivot.

