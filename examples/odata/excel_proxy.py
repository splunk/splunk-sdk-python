#!/usr/bin/env python
#
# Copyright 2011 Splunk, Inc.
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
# 

"""
This software embodies a splunkd proxy that translates communication
between a client application (browser, BI application, etc) and splunkd
"""

# installation support files
import os.path
import os
import sys
import urllib
import time
import xml.dom.minidom
import socket

# splunk support files
import splunk.binding as binding
from splunk.binding import connect

import utils

DEBUG = True

DEBUG_TEMPLATE = """\
  Python: %(python_version)s
  Python Path: %(python_path)s
  Platform: %(platform)s
  Absolute path of this script: %(abs_path)s
  Filename: %(filename)s
  WSGI Environment:
      %(wsgi_env)s
"""
ROW_DATA = "  %s -->> %r"
PORT = 8086

try:
    __file__
except NameError:
    __file__ = '?'


FD = None
if DEBUG:
    FD = open('./excel_proxy.debug', 'w')

def trace(string):
    """ trace something to the log file, if debug is on """
    if DEBUG:
        FD.write(string + "\n")
        FD.flush()


def get_local_ip():
    """ get the local ip address of this machine """

    # Nota Bene: this assume some sort of internet access
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("gmail.com", 80))
    return sock.getsockname()[0]

##
## The full atom RFC can be found here -- for reference
##
## http://tools.ietf.org/html/rfc4287
##

def convert_xml_to_atom(xml_text):
    """ splunk specific XML to Atom converter """

    ##
    ## Requires elements of <feed>:
    ## id:      Identifies the feed using a universally unique and permanent 
    ##          URI. If you have a long-term, renewable lease on your Internet
    ##          domain name, then use your website's address.
    ##          <id>http://host-name:8086</id>
    ## title:   Contains a human readable title for the feed. 
    ##          <title>Splunk event report</title>
    ## updated: Indicates the last time the feed was modified significantly.
    ##          <updated>2003-12-13T18:30:02Z</updated>
    ##

    ## Recommended elements of <feed>:
    ## author:  Names one author of the feed. 
    ##          <author>
    ##            <name>Splunk</name>
    ##          </author>
    ## link:    Identifies a related Web page. 
    ##          The type of relation is defined by the rel attribute. 
    ##          A feed is limited to one alternate per type and hreflang. 
    ##          A feed should contain a link back to the feed itself.
    ##          <link rel="self" href="/feed" />
    ##

    ## Optional elements of <feed>:
    ## category:Specifies a category that the feed belongs to. 
    ##          A feed may have multiple category elements.
    ##          <category term="sports"/>
    ## contributor: Names one contributor to the feed. 
    ##          An feed may have multiple contributor elements. 
    ##          <contributor>
    ##            <name>Jane Doe</name>
    ##          </contributor>
    ## generator: Identifies the software used to generate the feed, 
    ##          for debugging and other purposes. 
    ##          Both the uri and version attributes are optional.
    ##          <generator uri="/myblog.php" version="1.0">
    ##            Example Toolkit
    ##          </generator>
    ## icon:    Identifies a small image which provides iconic visual 
    ##          identification for the feed. Icons should be square.
    ##          <icon>/icon.jpg</icon>
    ## logo:    Identifies a larger image which provides visual identification 
    ##          for the feed. Images should be twice as wide as they are tall.
    ##          <logo>/logo.jpg</logo>
    ## rights:  Conveys information about rights, e.g. copyrights, held in 
    ##          and over the feed.
    ##          <rights type="html">
    ##            &amp;copy; 2005 John Doe
    ##          </rights>
    ## subtitle:Contains a human-readable description or subtitle of the feed. 
    ##          <subtitle>all your examples are belong to us</subtitle>`
    ##

    ## ****************************************************************

    ## Required elements of <entry>
    ## id:      Identifies the entry using a universally unique and 
    ##          permanent URI. Two entries in a feed can have the same value 
    ##          for id if they represent the same entry at different 
    ##          points in time.
    ##          <id>http://host-name:8086/xxx/yyyy</id>
    ## title:   Contains a human readable title for the entry.
    ##          <title>Splunk powered nanomites scour your IT</title>
    ## updated  Indicates the last time the entry was modified.
    ##          <updated>2003-12-13T18:30:02-05:00</updated>
    ##

    ## Recommended elements of <entry>
    ## author   Names one author of the entry.
    ##          <author>
    ##            <name>Splunk</name>
    ##          </author>
    ## content: Contains or links to the complete content of the entry. 
    ##          Content must be provided if there is no alternate link, 
    ##          and should be provided if there is no summary. 
    ##          <content>all the relevant information of this entry </content>
    ## link:    Identifies a related Web page. The type of relation is defined 
    ##          by the rel attribute. An entry is limited to one alternate per 
    ##          type and hreflang. An entry must contain an alternate link if 
    ##          there is no content element.
    ##          <link rel="alternate" href="/blog/1234"/>
    ## summary: Conveys a short summary, abstract, or excerpt of the entry. 
    ##          Summary should be provided if there either is no content 
    ##          provided for the entry, or that content is not inline 
    ##          (i.e., contains a src attribute), or if the content is encoded 
    ##          in base64.
    ##          <summary>Some text.</summary>
    ##

    ## Optional elements of <entry>
    ## category:Specifies a category that the entry belongs to. An entry may 
    ##          have multiple category elements.
    ##          <category term="data"/>
    ## contributor:Names one contributor to the entry. An entry may have 
    ##          multiple contributor elements. 
    ##          <contributor>
    ##            <name>Monty Python</name>
    ##          </contributor>
    ## published:Contains the time of the initial creation or 
    ##          first availability of the entry.
    ##          <published>2003-12-13T09:17:51-08:00</published>
    ## source:  If an entry is copied from one feed into another feed ...
    ##          <source>
    ##            <id>http://example.org/</id>
    ##            <title>Fourty-Two</title>
    ##            <updated>2003-12-13T18:30:02Z</updated>
    ##            <rights> &amp;copy 2011 Splunk, Inc.</rights>
    ##          </source>
    ## rights:  Conveys information about rights, e.g. copyrights, held in 
    ##          and over the feed.
    ##          <rights type="html">
    ##            &amp;copy; 2005 Monty Python
    ##          </rights>

    return xml_text

def fix_ids(doc):
    """ fixup identical ids to conform with Atom spec """

    ##
    ## without actually checking, guarantee that each id element is 
    ## unique by appending a monotonically increasing -<number> 
    ## to the of the id value
    ##

    count = 0
    ids = doc.getElementsByTagName("id")
    for xid in ids:
        if xid.firstChild and xid.firstChild.nodeType == 3: # text
            nodevalue = str(xid.firstChild.nodeValue) + "-%d" % count
            xid.removeChild(xid.firstChild)
            newchild = doc.createTextNode(nodevalue)
            xid.appendChild(newchild)
            count = count + 1

    return doc

def process_content(odata, atomcontent):
    """ lowest level fixup for atom-->odata """

    ##
    ## process the incoming atom and convert to excel friendly schema
    ##

    ##
    ## create an m:properties element that we populate with data
    ## from the s:dict 
    ##

    newcontent = odata.createElement("content")
    if atomcontent.hasAttributes():
        for attr in atomcontent.attributes.keys():
            newcontent.setAttribute(attr, atomcontent.getAttribute(attr))
    newprops = odata.createElement("m:properties")
    newtext = odata.createTextNode("\n      ")
    newcontent.appendChild(newtext)
    newcontent.appendChild(newprops)

    ##
    ## should only be one dictionary but convert the keys in the 
    ## dictionary to elements
    ##

    for prop in atomcontent.getElementsByTagName("s:dict"):
        newlist = []
        children = prop.childNodes
        for child in children:
            if child.attributes != None and child.firstChild != None:
                for key in child.attributes.keys():
                    if str(key) == "name":
                        name = str(child.getAttribute("name"))

                        ##
                        ## seems that parenthesis slashes and spaces found
                        ## in the atom make Odata unhappy, so here we
                        ## convert parens to dashes and strip the slash
                        ##

                        name = name.replace("(", "_")
                        name = name.replace(")", "_")
                        name = name.replace("/", "_")
                        name = name.replace(" ", "_")
                        value = str(child.firstChild.nodeValue)
                        newelement = odata.createElement("d:"+name)
                        newtext = odata.createTextNode(value)
                        newelement.appendChild(newtext)
                        newlist.append(newelement)
            else:
                newlist.append(child)
        for child in newlist:
            newprops.appendChild(child)

    newtext = odata.createTextNode("\n    ")
    newcontent.appendChild(newtext)

    return newcontent

def process_entry(odata, entry):
    """ process the splunk entry data """

    ##
    ## change s:dict to m:properties
    ## change the keys to elements
    ##

    newentry = odata.createElement("entry")

    for child in entry.childNodes:
        if child.nodeName == "content":
            newentry.appendChild(process_content(odata, child))
        else:
            newentry.appendChild(child.cloneNode(True))

    return newentry
    
def fixup_to_msft_schema(fixed_xml, title):
    """ transform the splunk schema to msft schema """

    ##
    ## for powerpivot/excel parsing and interpretation
    ## add in the microsoft schema and then munge the named multi-key
    ## elements to individually named elements
    ##

    try:
        doc = xml.dom.minidom.parseString(fixed_xml)
    except xml.parsers.expat.ExpatError:
        # if we fail to parser the XML, return an empty feed 
        trace("Error: xml failed to parse via xml.dom.minidom")
        trace("failing XML is as follows, returning empty XML feed instead:")
        trace(str(fixed_xml))
        # return an empty collection
        return "<?xml version='1.0' encoding='UTF-8'?>"+\
          '<feed xmlns="http://www.w3.org/2005/Atom" '+\
          'xmlns:s="http://dev.splunk.com/ns/rest" '+\
          'xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">'+\
          '<title>dummy</title>'+\
          '<id>https://127.0.0.1/servicesNS/admin/search/saved/searches</id>'+\
          '<updated>2011-04-25T14:18:54-07:00</updated>'+\
          '<generator version="97641"/>'+\
          '<author>'+\
          '<name>Splunk</name>'+\
          '</author>'+\
          '</feed>' 

    ##
    ## <id></id> must be unique within a feed, AND be a complete
    ##     URL (i.e. partial URL is insufficent)
    ##
    ##     <id>/services/search/jobs/1303147485.159</id>
    ##     changes to:
    ##     <id>http://DNSname/services/search/jobs/1303147485.159</id>
    ##
    ##     and that there cannot be multiple id's with the same value
    ##
    ##     <id>http://DNSname/services/search/jobs/1303147485.159</id>
    ##     changes to (add -[Number])
    ##     <id>http://DNSname/services/search/jobs/1303147485.159-1</id>
    ##
    ##     So says the Atom 1.0 verifiers
    ##

    doc = fix_ids(doc)

    odata = xml.dom.minidom.Document()

    ##
    ## assume the feed is of the form we are expecting: 
    ## xml-stylesheet, feed
    ##

    for child in doc.childNodes:
        if str(child.nodeName) == "xml-stylesheet":
            instr = child.cloneNode(True)
        elif str(child.nodeName) == "feed":
            ofeed = child
            feed = child.cloneNode(False)

    # attach the children
    odata.appendChild(instr)
    odata.appendChild(feed)

    # add the msft data schemas 
    feed.setAttribute("xmlns:d", "http://schemas.microsoft.com/ado/2007/08/dataservices")
    feed.setAttribute("xmlns:m", "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata")

    ##
    ## we don't expect a link element, so add one, prefaced with 
    ## a little whitespace
    ##

    newtext = odata.createTextNode("\n  ")
    feed.appendChild(newtext)
    
    link = odata.createElement("link")

    if title:
        title = title.replace("/","/Catalog/")
        link.setAttribute("rel", "self")
        link.setAttribute("title", title)
        link.setAttribute("href", title)
        feed.appendChild(link)

    ##
    ## loop through all the child nodes of feed, and adjust as necessary
    ## we expect (as high level child nodes):
    ## title, id, updated, generator version, author and then zero or 
    ## more entries we can skip processing any of the next nodes: they 
    ## are just whitespace so simply tack them on
    ##

    for child in ofeed.childNodes:
        if child.nodeType != 3:
            if str(child.nodeName) == "title":
                feed.appendChild(child.cloneNode(True))
            elif str(child.nodeName) == "id":
                feed.appendChild(child.cloneNode(True))
            elif str(child.nodeName) == "updated":
                feed.appendChild(child.cloneNode(True))
            elif str(child.nodeName) == "generator":
                feed.appendChild(child.cloneNode(True))
            elif str(child.nodeName) == "author":
                feed.appendChild(child.cloneNode(True))
            elif str(child.nodeName) == "entry":
                feed.appendChild(process_entry(odata, child))
            else:
                trace("WARNING: unknown node: %s" % str(child.nodeName))
        else:
            feed.appendChild(child.cloneNode(True))

    fixed_xml = str(odata.toxml())

    return fixed_xml

def fix_xml(xml_text, title=None):
    """ fixup broken XML """

    ##
    ## this function detects broken XML and tries to fix it up.
    ## using emprical evidence, fix up things we have 
    ## seen before as broken XML
    ##

    fixed_xml = xml_text

    # 1. does it parse?
    try:
        xml.dom.minidom.parseString(xml_text)
    except xml.parsers.expat.ExpatError:

        ##
        ## got exception, so look for multi-result-previews
        ## and if found, add an outside wrapper
        ##

        xml_decl = "<?xml version='1.0' encoding='UTF-8'?>"
        result_preview = "<results preview='0'>"
        outer_wrapper_start = "<splunk_outer_wrapper>"
        outer_wrapper_end = "</splunk_outer_wrapper>"

        index = xml_text.find(result_preview)
        if index > 0:
            next_index = xml_text.find(result_preview, index+1)
            if next_index > 0:
                # build outer wrapper
                fixed_xml = xml_decl + "\n"
                fixed_xml += outer_wrapper_start
                fixed_xml += xml_text.replace(xml_decl, "", 1)
                fixed_xml += outer_wrapper_end

    # 2. multiple fix/conversions for Odata

    fixed_xml = fixup_to_msft_schema(fixed_xml, title)

    # 3. <test condition> [TBD]

    return fixed_xml

def debug_connect(environ):
    """ optionally print some debug info on connection by client """

    # conditionally generate debug printing
    debugdata = DEBUG_TEMPLATE % {
      'python_version': sys.version,
      'platform': sys.platform,
      'abs_path': os.path.abspath('.'),
      'filename': __file__,
      'python_path': repr(sys.path),
      'wsgi_env': '\n'.join([ROW_DATA % item for item in environ.items()]),
    }

    trace("Context data:\n%s\n" % debugdata)

def wait_for_search(context, url):
    """ when POSTing, wait for a finished splunk response """

    trace("wait_for_search: %s, %s" % (context, url))

    # if posting, wait on the object to be finished.
    # nota bene: this could be dangerous if there is a different kind
    #            of error other than 404
    while True:
        data = context.get(url)
        if data["status"] == 404:
            trace("Waiting for search on URL: %s failed with 404" % url)
            return
        if data["status"] != 204: # skip no-body returns
            pxml = xml.dom.minidom.parseString(data.body.read())
            for key in pxml.getElementsByTagName("s:key"):
                if key.getAttribute("name") == "isDone":
                    if key.firstChild.nodeValue == "1":
                        return
        time.sleep(1)

def post_catalog_search(context, endpoint):
    """ post a catalog search, wait for response """

    # generate a real splunkd endpoint from our incoming catalog
    endpoint = "/services/saved/searches%s/dispatch" % endpoint
    trace("post_catalog_search: %s, %s" % (context, endpoint))

    # get the session id
    sid_xml_text = context.post(endpoint).body.read()
    sid_xml = xml.dom.minidom.parseString(sid_xml_text)
    sid = str(sid_xml.getElementsByTagName("sid")[0].firstChild.nodeValue)

    # wait on the endopint return
    endpoint = "/services/search/jobs/" + sid
    wait_for_search(context, endpoint)

    # search has completed, get the data and return
    endpoint = endpoint + "/results"
    return context.get(endpoint, output_mode="atom")

def post_query(context, endpoint, query=None):
    """ post a query, wait for response """

    # hack for tableau
    query = query.replace("$inlinecount=allpages&$top=1&", "", 1)
    query = query.replace("$top=1&", "", 1)

    # generate a real splunkd request from the request
    trace("post_query : %s, %s, %s" % (context, endpoint, query))

    # remove double search
    if query:
        query = query.replace("search=", "", 1)

    # get the session id
    sid_xml_text = context.post(endpoint, search=query).body.read()
    sid_xml = xml.dom.minidom.parseString(sid_xml_text)
    sid = str(sid_xml.getElementsByTagName("sid")[0].firstChild.nodeValue)

    # wait in the endpoint return
    endpoint = endpoint + "/" + sid
    wait_for_search(context, endpoint)

    # search has completed, get the data and return
    endpoint = endpoint + "/results"
    return context.get(endpoint, output_mode="atom")

def get_splunk_catalog(context):
    """ http GET the saved jobs endpoint and build Odata style catalog """

    # generate an Odata ctalog from splunkd's saved searches
    data = context.get("/services/saved/searches") 
    body = data.body.read()

    bxml = xml.dom.minidom.parseString(body)
    catalog = xml.dom.minidom.Document()

    # create root service
    rootelement = catalog.createElement("service")
    rootelement.setAttribute("xml:base",
                             "http://%s:%s/Catalog/" % (get_local_ip(), PORT))
    rootelement.setAttribute("xmlns:atom",
                             "http://www.w3.org/2005/Atom")
    rootelement.setAttribute("xmlns:app",
                             "http://www.w3.org/2007/app")
    rootelement.setAttribute("xmlns",
                             "http://www.w3.org/2007/app")

    catalog.appendChild(rootelement)

    # add in the workspace
    workspace = catalog.createElement("workspace")
    rootelement.appendChild(workspace)

    # add high level title
    maintitle = catalog.createElement("atom:title")
    text = catalog.createTextNode("Splunk Catalog")
    maintitle.appendChild(text)
    workspace.appendChild(maintitle)

    ##
    ## pull apart each splunk saved search and build as:
    ##
    ## <collection href="<reference to save searc>">\
    ##   <atom:title><name of saved search></atom:title>\
    ## </collection>\
    ##

    entries = bxml.getElementsByTagName("entry")
    for entry in entries:
        # get existing 
        title = entry.getElementsByTagName("title")[0]
        text_title = str(title.firstChild.nodeValue)

        # build
        #href = "/catalog/services/saved/searches/%s/dispatch" % text_title
        collection = catalog.createElement("collection")
        collection.setAttribute("href", "%s" % text_title)

        xtitle = catalog.createElement("atom:title")
        text = catalog.createTextNode("%s" % text_title)
        xtitle.appendChild(text)
        collection.appendChild(xtitle)

        workspace.appendChild(collection)

    return (data, str(catalog.toxml()))

def application(environ, start_response):
    """ The splunk proxy processor """

    debug_connect(environ)

    # extract some basic HTTP/WSGI info
    endpoint = environ["PATH_INFO"]
    query = environ["QUERY_STRING"]

    # perform idempotent login/connect -- get login creds from ~/.splunkrc
    opts = utils.parse(sys.argv[1:], {}, ".splunkrc")
    connection = connect(**opts.kwargs)

    # get lower level context
    context = binding.connect( host=connection.host, 
                               username=connection.username,
                               password=connection.password)

    ##
    ## here we can/should/must look up the endpoint and decide what operation
    ## needs to be done -- for now we simply "get" for basic urls, and 
    ## look for a special "search" in the query (if present) and build a job 
    ## out of it. We also look for special Odata (excel) Catalog lookups
    ## 
    ## in particular, we want to look for:
    ##
    ## /services/search/jobs
    ##
    
    if endpoint.lower() == "/catalog" or endpoint.lower() == "/catalog/":
        # here we fabricate a catalog endpoint
        trace("OData catalog get")
        (data, body) = get_splunk_catalog(context)
    elif endpoint.lower().find("/catalog/") == 0:
        # we have a full-on catalog query/search
        # remove the pre-pended catalog
        endpoint = endpoint.replace("/Catalog","")
        title = endpoint
        # quote the special characters, and post the search
        endpoint = urllib.quote(endpoint)
        trace("OData catalog dispatch: %s" % endpoint)
        data = post_catalog_search(context, endpoint)

        # fixup query results 
        body = str(data.body.read())
        trace("Splunk generated Atom/XML before fixup is:")
        trace(body)
        body = fix_xml(body, title)
    elif query:
        trace("raw query: base: %s, query: %s" % (endpoint, query))

        ##
        ## sanitize query, and issue
        ##
        ## this is a little awkward, browsers and BI apps seem to sanitize the 
        ## query string(s) which doesn't get accepted by splunkd. So we unquote
        ## the original and rebuild it the way we would like to see it.
        ##

        query = urllib.unquote(query)
        endpoint = urllib.quote(endpoint)

        if endpoint == "/services/search/jobs":
            data = post_query(context, endpoint, query=query)
            # fixup query results 
            body = fix_xml(data.body.read())
        else:
            data = context.get(endpoint, search=query) 
            body = data.body.read()
    else:
        # catch all for passthrough
        trace("request passthrough endpoint: %s" % endpoint)
        data = context.get(endpoint) 
        body = data.body.read()

    # extract the status and headers from the splunk operation 
    status = str(data["status"]) + " " + data["reason"]
    headers = data["headers"]

    trace("Returning Atom/XML:\n")
    trace(body + "\n")

    ##
    ## clean hop-by-hop from headers (described in section 13.5.1 of RFC2616),
    ## and adjust the header length if modified by fix_xml()
    ##

    for thing in headers:
        if thing[0] == "connection":
            headers.remove(thing)
        if thing[0] == "content-length":
            headers.remove(thing)
            headers.insert(0, ("content-length", str(len(body))))

    # start the response (retransmit the status and headers)
    start_response(status, headers)

    return [body]

if __name__ == '__main__':
    # this script only runs when started directly from a shell
    try:
        # create a simple WSGI server and run the splunk proxy processor
        from wsgiref import simple_server
        print "splunk proxy: connect to http://%s:%d/..." % (get_local_ip(), PORT)
        HTTPD = simple_server.WSGIServer(('', PORT), 
                                         simple_server.WSGIRequestHandler)
        HTTPD.set_app(application)
        HTTPD.serve_forever()
    except ImportError:
        # wsgiref not installed, just output html to stdout
        for content in application({}, lambda status, headers: None):
            print content
