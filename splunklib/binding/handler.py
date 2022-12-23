import ssl
from http import client

from .ResponseReader import ResponseReader
from .utils import _spliturl


def handler(key_file=None, cert_file=None, timeout=None, verify=False, context=None):
    """This class returns an instance of the default HTTP request handler using
    the values you provide.

    :param `key_file`: A path to a PEM (Privacy Enhanced Mail) formatted file containing your private key (optional).
    :type key_file: ``string``
    :param `cert_file`: A path to a PEM (Privacy Enhanced Mail) formatted file containing a certificate chain file (optional).
    :type cert_file: ``string``
    :param `timeout`: The request time-out period, in seconds (optional).
    :type timeout: ``integer`` or "None"
    :param `verify`: Set to False to disable SSL verification on https connections.
    :type verify: ``Boolean``
    :param `context`: The SSLContext that can is used with the HTTPSConnection when verify=True is enabled and context is specified
    :type context: ``SSLContext`
    """

    def connect(scheme, host, port):
        kwargs = {}
        if timeout is not None: kwargs['timeout'] = timeout
        if scheme == "http":
            return client.HTTPConnection(host, port, **kwargs)
        if scheme == "https":
            if key_file is not None:
                kwargs['key_file'] = key_file
            if cert_file is not None:
                kwargs['cert_file'] = cert_file

            if not verify:
                kwargs['context'] = ssl._create_unverified_context()
            elif context:
                # verify is True in elif branch and context is not None
                kwargs['context'] = context

            return client.HTTPSConnection(host, port, **kwargs)
        raise ValueError(f"unsupported scheme: {scheme}")

    def request(url, message, **kwargs):
        scheme, host, port, path = _spliturl(url)
        body = message.get("body", "")
        head = {
            "Content-Length": str(len(body)),
            "Host": host,
            "User-Agent": "splunk-sdk-python/1.7.2",
            "Accept": "*/*",
            "Connection": "Close",
        }  # defaults
        for key, value in message["headers"]:
            head[key] = value
        method = message.get("method", "GET")

        connection = connect(scheme, host, port)
        is_keepalive = False
        try:
            connection.request(method, path, body, head)
            if timeout is not None:
                connection.sock.settimeout(timeout)
            response = connection.getresponse()
            is_keepalive = "keep-alive" in response.getheader("connection", default="close").lower()
        finally:
            if not is_keepalive:
                connection.close()

        return {
            "status": response.status,
            "reason": response.reason,
            "headers": response.getheaders(),
            "body": ResponseReader(response, connection if is_keepalive else None),
        }

    return request
