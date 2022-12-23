import logging
from datetime import datetime
from contextlib import contextmanager
from functools import wraps
from http.cookies import SimpleCookie
from urllib import parse

from .UrlEncoded import UrlEncoded
from .NoAuthenticationToken import _NoAuthenticationToken
from splunklib.data import Record
from splunklib.exceptions import HTTPError, AuthenticationError
from splunklib.constants import DEFAULT_HOST, DEFAULT_SCHEME, DEFAULT_PORT

logger = logging.getLogger(__name__)


def _log_duration(f):
    @wraps(f)
    def new_f(*args, **kwargs):
        start_time = datetime.now()
        val = f(*args, **kwargs)
        end_time = datetime.now()
        logger.debug("Operation took %s", end_time - start_time)
        return val

    return new_f


def _parse_cookies(cookie_str, dictionary):
    """Tries to parse any key-value pairs of cookies in a string,
    then updates the the dictionary with any key-value pairs found.

    **Example**::

        dictionary = {}
        _parse_cookies('my=value', dictionary)
        # Now the following is True
        dictionary['my'] == 'value'

    :param cookie_str: A string containing "key=value" pairs from an HTTP "Set-Cookie" header.
    :type cookie_str: ``str``
    :param dictionary: A dictionary to update with any found key-value pairs.
    :type dictionary: ``dict``
    """
    parsed_cookie = SimpleCookie(cookie_str)
    for cookie in list(parsed_cookie.values()):
        dictionary[cookie.key] = cookie.coded_value


def _make_cookie_header(cookies):
    """
    Takes a list of 2-tuples of key-value pairs of
    cookies, and returns a valid HTTP ``Cookie``
    header.

    **Example**::

        header = _make_cookie_header([("key", "value"), ("key_2", "value_2")])
        # Now the following is True
        header == "key=value; key_2=value_2"

    :param cookies: A list of 2-tuples of cookie key-value pairs.
    :type cookies: ``list`` of 2-tuples
    :return: ``str` An HTTP header cookie string.
    :rtype: ``str``
    """
    return "; ".join(f"{key}={value}" for key, value in cookies)


@contextmanager
def _handle_auth_error(msg):
    """Handle re-raising HTTP authentication errors as something clearer.

    If an ``HTTPError`` is raised with status 401 (access denied) in
    the body of this context manager, re-raise it as an
    ``AuthenticationError`` instead, with *msg* as its message.

    This function adds no round trips to the server.

    :param msg: The message to be raised in ``AuthenticationError``.
    :type msg: ``str``

    **Example**::

        with _handle_auth_error("Your login failed."):
             ... # make an HTTP request
    """
    try:
        yield
    except HTTPError as he:
        if he.status == 401:
            raise AuthenticationError(msg, he)
        else:
            raise


def _authentication(request_fun):
    """Decorator to handle autologin and authentication errors.

    *request_fun* is a function taking no arguments that needs to
    be run with this ``Context`` logged into Splunk.

    ``_authentication``'s behavior depends on whether the
    ``autologin`` field of ``Context`` is set to ``True`` or
    ``False``. If it's ``False``, then ``_authentication``
    aborts if the ``Context`` is not logged in, and raises an
    ``AuthenticationError`` if an ``HTTPError`` of status 401 is
    raised in *request_fun*. If it's ``True``, then
    ``_authentication`` will try at all sensible places to
    log in before issuing the request.

    If ``autologin`` is ``False``, ``_authentication`` makes
    one roundtrip to the server if the ``Context`` is logged in,
    or zero if it is not. If ``autologin`` is ``True``, it's less
    deterministic, and may make at most three roundtrips (though
    that would be a truly pathological case).

    :param request_fun: A function of no arguments encapsulating
                        the request to make to the server.

    **Example**::

        import splunklib.binding as binding
        c = binding.connect(..., autologin=True)
        c.logout()
        def f():
            c.get("/services")
            return 42
        print(_authentication(f))
    """

    @wraps(request_fun)
    def wrapper(self, *args, **kwargs):
        if self.token is _NoAuthenticationToken and not self.has_cookies():
            # Not yet logged in.
            if self.autologin and self.username and self.password:
                # This will throw an uncaught
                # AuthenticationError if it fails.
                self.login()
            else:
                # Try the request anyway without authentication.
                # Most requests will fail. Some will succeed, such as
                # 'GET server/info'.
                with _handle_auth_error("Request aborted: not logged in."):
                    return request_fun(self, *args, **kwargs)
        try:
            # Issue the request
            return request_fun(self, *args, **kwargs)
        except HTTPError as he:
            if he.status == 401 and self.autologin:
                # Authentication failed. Try logging in, and then
                # rerunning the request. If either step fails, throw
                # an AuthenticationError and give up.
                with _handle_auth_error("Autologin failed."):
                    self.login()
                with _handle_auth_error(
                        "Authentication Failed! If session token is used, it seems to have been expired."):
                    return request_fun(self, *args, **kwargs)
            elif he.status == 401 and not self.autologin:
                raise AuthenticationError(
                    "Request failed: Session is not logged in.", he)
            else:
                raise

    return wrapper


def _authority(scheme=DEFAULT_SCHEME, host=DEFAULT_HOST, port=DEFAULT_PORT):
    """Construct a URL authority from the given *scheme*, *host*, and *port*.

    Named in accordance with RFC2396_, which defines URLs as::

        <scheme>://<authority><path>?<query>

    .. _RFC2396: http://www.ietf.org/rfc/rfc2396.txt

    So ``https://localhost:8000/a/b/b?boris=hilda`` would be parsed as::

        scheme := https
        authority := localhost:8000
        path := /a/b/c
        query := boris=hilda

    :param scheme: URL scheme (the default is "https")
    :type scheme: "http" or "https"
    :param host: The host name (the default is "localhost")
    :type host: string
    :param port: The port number (the default is 8089)
    :type port: integer
    :return: The URL authority.
    :rtype: UrlEncoded (subclass of ``str``)

    **Example**::

        _authority() == "https://localhost:8089"

        _authority(host="splunk.utopia.net") == "https://splunk.utopia.net:8089"

        _authority(host="2001:0db8:85a3:0000:0000:8a2e:0370:7334") == \
            "https://[2001:0db8:85a3:0000:0000:8a2e:0370:7334]:8089"

        _authority(scheme="http", host="splunk.utopia.net", port="471") == \
            "http://splunk.utopia.net:471"

    """
    if ':' in host:
        # IPv6 addresses must be enclosed in [ ] in order to be well-formed.
        host = '[' + host + ']'
    return UrlEncoded(f"{scheme}://{host}:{port}", skip_encode=True)


# kwargs: sharing, owner, app
def namespace(sharing=None, owner=None, app=None, **kwargs):
    """This function constructs a Splunk namespace.

    Every Splunk resource belongs to a namespace. The namespace is specified by
    the pair of values ``owner`` and ``app`` and is governed by a ``sharing`` mode.
    The possible values for ``sharing`` are: "user", "app", "global" and "system",
    which map to the following combinations of ``owner`` and ``app`` values:

        "user"   => {owner}, {app}

        "app"    => nobody, {app}

        "global" => nobody, {app}

        "system" => nobody, system

    "nobody" is a special user name that basically means no user, and "system"
    is the name reserved for system resources.

    "-" is a wildcard that can be used for both ``owner`` and ``app`` values and
    refers to all users and all apps, respectively.

    In general, when you specify a namespace you can specify any combination of
    these three values and the library will reconcile the triple, overriding the
    provided values as appropriate.

    Finally, if no namespacing is specified the library will make use of the
    ``/services`` branch of the REST API, which provides a namespaced view of
    Splunk resources equivelent to using ``owner={currentUser}`` and
    ``app={defaultApp}``.

    The ``namespace`` function returns a representation of the namespace from
    reconciling the values you provide. It ignores any keyword arguments other
    than ``owner``, ``app``, and ``sharing``, so you can provide ``dicts`` of
    configuration information without first having to extract individual keys.

    :param sharing: The sharing mode (the default is "user").
    :type sharing: "system", "global", "app", or "user"
    :param owner: The owner context (the default is "None").
    :type owner: ``string``
    :param app: The app context (the default is "None").
    :type app: ``string``
    :returns: A :class:`splunklib.data.Record` containing the reconciled
        namespace.

    **Example**::

        import splunklib.binding as binding
        n = binding.namespace(sharing="user", owner="boris", app="search")
        n = binding.namespace(sharing="global", app="search")
    """
    if sharing in ["system"]:
        return Record({'sharing': sharing, 'owner': "nobody", 'app': "system"})
    if sharing in ["global", "app"]:
        return Record({'sharing': sharing, 'owner': "nobody", 'app': app})
    if sharing in ["user", None]:
        return Record({'sharing': sharing, 'owner': owner, 'app': app})
    raise ValueError("Invalid value for argument: 'sharing'")


# Encode the given kwargs as a query string. This wrapper will also _encode
# a list value as a sequence of assignments to the corresponding arg name,
# for example an argument such as 'foo=[1,2,3]' will be encoded as
# 'foo=1&foo=2&foo=3'.
def _encode(**kwargs):
    items = []
    for key, value in list(kwargs.items()):
        if isinstance(value, list):
            items.extend([(key, item) for item in value])
        else:
            items.append((key, value))
    return parse.urlencode(items)


# Crack the given url into (scheme, host, port, path)
def _spliturl(url):
    parsed_url = parse.urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port
    path = '?'.join((parsed_url.path, parsed_url.query)) if parsed_url.query else parsed_url.path
    # Strip brackets if its an IPv6 address
    if host.startswith('[') and host.endswith(']'): host = host[1:-1]
    if port is None:
        port = DEFAULT_PORT
    return parsed_url.scheme, host, port, path
