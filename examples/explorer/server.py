#!/usr/bin/env python
#
# Copyright 2011-2015 Splunk, Inc.
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

import SimpleHTTPServer
import SocketServer
import urllib2
import sys
import StringIO

PORT = 8080

class RedirectHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        redirect_url, headers = self.get_url_and_headers()
        if redirect_url is None:
            return

        # Append the GET parameters to the URL
        redirect_url += self.path

        # Make sure we replace any instance of // with /
        redirect_url.replace("//", "/")

        self.make_request(redirect_url, "GET", None, headers)
    
    def do_POST(self):
        redirect_url, headers = self.get_url_and_headers()

        # Get the POST data
        length = int(self.headers.getheader('content-length'))
        data = self.rfile.read(length)

        self.make_request(redirect_url, "POST", data, headers)

    def do_DELETE(self):
        redirect_url, headers = self.get_url_and_headers()

        self.make_request(redirect_url, "DELETE", "", headers)

    def do_OPTIONS(self):
        # This is some capability checking, so we only need to send the cross domain
        # headers to show that it's all good
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "PUT, POST, GET, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "X-Redirect-URL, Authorization")
        self.end_headers()

    def get_url_and_headers(self):
        # Collect all the headers
        headers = {}
        for header_name in self.headers.keys():
            headers[header_name] = self.headers.getheader(header_name)

        # Get the redirect URL and remove it from the headers
        redirect_url = None
        if headers.has_key("x-redirect-url"):
            redirect_url = headers["x-redirect-url"]
            del headers["x-redirect-url"]
        else:
            self.send_error(500, "Request is missing X-Redirect-URL header.")

        return (redirect_url, headers)

    def make_request(self, url, method, data, headers):
        self.log_message("%s: %s", method, url)

        try:
            # Make the request
            request = urllib2.Request(url, data, headers)
            request.get_method = lambda: method
            response = urllib2.urlopen(request)

            # We were successful, so send the response code
            self.send_response(response.code, message=response.msg)
            for key, value in dict(response.headers).iteritems():
                # Optionally log the headers
                #self.log_message("%s: %s" % (key, value))

                self.send_header(key, value)
            
            # Send the cross-domain headers
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "PUT, POST, GET, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "X-Redirect-URL, Authorization")

            # We are done with the headers
            self.end_headers()

            # Copy the response to the output
            self.copyfile(response, self.wfile)
        except urllib2.HTTPError as e:
            # On errors, log the response code and message
            self.log_message("Code: %s (%s)", e.code, e.msg)

            for key, value in dict(e.hdrs).iteritems():
                # On errors, we always log the headers
                self.log_message("%s: %s", key, value)

            response_text = e.fp.read()
            response_file = StringIO.StringIO(response_text)

            # On errors, we also log the response text
            self.log_message("Response: %s", response_text)

            # Send the error response code
            self.send_response(e.code, message=e.msg)

            # Send the cross-domain headers
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "PUT, POST, GET, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "X-Redirect-URL, Authorization")

            # Send the other headers
            self.send_header("Content-Type", self.error_content_type)
            self.send_header('Connection', 'close')
            self.end_headers()

            # Finally, send the error itself
            self.copyfile(response_file, self.wfile)
        
class ReuseableSocketTCPServer(SocketServer.TCPServer):
    def __init__(self, *args, **kwargs):
        self.allow_reuse_address = True
        SocketServer.TCPServer.__init__(self, *args, **kwargs)

def serve(port = PORT):
    Handler = RedirectHandler
    
    httpd = ReuseableSocketTCPServer(("", int(port)), Handler)
    
    print "API Explorer -- Port: %s" % int(port)
    
    httpd.serve_forever()

def main(argv):
    if (len(argv) > 0):
        port = argv[0]
        serve(port = PORT)
    else:
        serve()
        
if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
    except:
        raise
