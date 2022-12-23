from datetime import datetime, timedelta
from time import sleep

from .BaseService import _BaseService
from .utils import _load_atom, _filter_content
from splunklib.collection import *
from splunklib.data.utils import load
from splunklib.entity import *
from splunklib.exceptions import IllegalOperationException

from splunklib.constants import PATH_MODULAR_INPUTS, PATH_MESSAGES, MATCH_ENTRY_CONTENT, PATH_INDEXES, PATH_APPS, \
    PATH_CAPABILITIES, PATH_FIRED_ALERTS, PATH_EVENT_TYPES


class Service(_BaseService):
    """A Pythonic binding to Splunk instances.

    A :class:`Service` represents a binding to a Splunk instance on an
    HTTP or HTTPS port. It handles the details of authentication, wire
    formats, and wraps the REST API endpoints into something more
    Pythonic. All of the low-level operations on the instance from
    :class:`splunklib.binding.Context` are also available in case you need
    to do something beyond what is provided by this class.

    After creating a ``Service`` object, you must call its :meth:`login`
    method before you can issue requests to Splunk.
    Alternately, use the :func:`connect` function to create an already
    authenticated :class:`Service` object, or provide a session token
    when creating the :class:`Service` object explicitly (the same
    token may be shared by multiple :class:`Service` objects).

    :param host: The host name (the default is "localhost").
    :type host: ``string``
    :param port: The port number (the default is 8089).
    :type port: ``integer``
    :param scheme: The scheme for accessing the service (the default is "https").
    :type scheme: "https" or "http"
    :param verify: Enable (True) or disable (False) SSL verification for
                   https connections. (optional, the default is True)
    :type verify: ``Boolean``
    :param `owner`: The owner context of the namespace (optional; use "-" for wildcard).
    :type owner: ``string``
    :param `app`: The app context of the namespace (optional; use "-" for wildcard).
    :type app: ``string``
    :param `token`: The current session token (optional). Session tokens can be
                    shared across multiple service instances.
    :type token: ``string``
    :param cookie: A session cookie. When provided, you don't need to call :meth:`login`.
        This parameter is only supported for Splunk 6.2+.
    :type cookie: ``string``
    :param `username`: The Splunk account username, which is used to
                       authenticate the Splunk instance.
    :type username: ``string``
    :param `password`: The password, which is used to authenticate the Splunk
                       instance.
    :type password: ``string``
    :param retires: Number of retries for each HTTP connection (optional, the default is 0).
                    NOTE THAT THIS MAY INCREASE THE NUMBER OF ROUND TRIP CONNECTIONS TO THE SPLUNK SERVER.
    :type retries: ``int``
    :param retryDelay: How long to wait between connection attempts if `retries` > 0 (optional, defaults to 10s).
    :type retryDelay: ``int`` (in seconds)
    :return: A :class:`Service` instance.

    **Example**::

        import splunklib.client as client
        s = client.Service(username="boris", password="natasha", ...)
        s.login()
        # Or equivalently
        s = client.connect(username="boris", password="natasha")
        # Or if you already have a session token
        s = client.Service(token="atg232342aa34324a")
        # Or if you already have a valid cookie
        s = client.Service(cookie="splunkd_8089=...")
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._splunk_version = None
        self._kvstore_owner = None
        self._instance_type = None

    @property
    def apps(self):
        """Returns the collection of applications that are installed on this instance of Splunk.

        :return: A :class:`Collection` of :class:`Application` entities.
        """
        return Collection(self, PATH_APPS, item=Application)

    @property
    def confs(self):
        """Returns the collection of configuration files for this Splunk instance.

        :return: A :class:`Configurations` collection of
            :class:`ConfigurationFile` entities.
        """
        return Configurations(self)

    @property
    def capabilities(self):
        """Returns the list of system capabilities.

        :return: A ``list`` of capabilities.
        """
        response = self.get(PATH_CAPABILITIES)
        return _load_atom(response, MATCH_ENTRY_CONTENT).capabilities

    @property
    def event_types(self):
        """Returns the collection of event types defined in this Splunk instance.

        :return: An :class:`Entity` containing the event types.
        """
        return Collection(self, PATH_EVENT_TYPES)

    @property
    def fired_alerts(self):
        """Returns the collection of alerts that have been fired on the Splunk
        instance, grouped by saved search.

        :return: A :class:`Collection` of :class:`AlertGroup` entities.
        """
        return Collection(self, PATH_FIRED_ALERTS, item=AlertGroup)

    @property
    def indexes(self):
        """Returns the collection of indexes for this Splunk instance.

        :return: An :class:`Indexes` collection of :class:`Index` entities.
        """
        return Indexes(self, PATH_INDEXES, item=Index)

    @property
    def info(self):
        """Returns the information about this instance of Splunk.

        :return: The system information, as key-value pairs.
        :rtype: ``dict``
        """
        response = self.get("/services/server/info")
        return _filter_content(_load_atom(response, MATCH_ENTRY_CONTENT))

    def input(self, path, kind=None):
        """Retrieves an input by path, and optionally kind.

        :return: A :class:`Input` object.
        """
        return Input(self, path, kind=kind).refresh()

    @property
    def inputs(self):
        """Returns the collection of inputs configured on this Splunk instance.

        :return: An :class:`Inputs` collection of :class:`Input` entities.
        """
        return Inputs(self)

    def job(self, sid):
        """Retrieves a search job by sid.

        :return: A :class:`Job` object.
        """
        return Job(self, sid).refresh()

    @property
    def jobs(self):
        """Returns the collection of current search jobs.

        :return: A :class:`Jobs` collection of :class:`Job` entities.
        """
        return Jobs(self)

    @property
    def loggers(self):
        """Returns the collection of logging level categories and their status.

        :return: A :class:`Loggers` collection of logging levels.
        """
        return Loggers(self)

    @property
    def messages(self):
        """Returns the collection of service messages.

        :return: A :class:`Collection` of :class:`Message` entities.
        """
        return Collection(self, PATH_MESSAGES, item=Message)

    @property
    def modular_input_kinds(self):
        """Returns the collection of the modular input kinds on this Splunk instance.

        :return: A :class:`ReadOnlyCollection` of :class:`ModularInputKind` entities.
        """
        if self.splunk_version >= (5,):
            return ReadOnlyCollection(self, PATH_MODULAR_INPUTS, item=ModularInputKind)
        raise IllegalOperationException("Modular inputs are not supported before Splunk version 5.")

    @property
    def storage_passwords(self):
        """Returns the collection of the storage passwords on this Splunk instance.

        :return: A :class:`ReadOnlyCollection` of :class:`StoragePasswords` entities.
        """
        return StoragePasswords(self)

    # kwargs: enable_lookups, reload_macros, parse_only, output_mode
    def parse(self, query, **kwargs):
        """Parses a search query and returns a semantic map of the search.

        :param query: The search query to parse.
        :type query: ``string``
        :param kwargs: Arguments to pass to the ``search/parser`` endpoint
            (optional). Valid arguments are:

            * "enable_lookups" (``boolean``): If ``True``, performs reverse lookups
              to expand the search expression.

            * "output_mode" (``string``): The output format (XML or JSON).

            * "parse_only" (``boolean``): If ``True``, disables the expansion of
              search due to evaluation of subsearches, time term expansion,
              lookups, tags, eventtypes, and sourcetype alias.

            * "reload_macros" (``boolean``): If ``True``, reloads macro
              definitions from macros.conf.

        :type kwargs: ``dict``
        :return: A semantic map of the parsed search query.
        """
        if not self.disable_v2_api:
            return self.post("search/v2/parser", q=query, **kwargs)
        return self.get("search/parser", q=query, **kwargs)

    def restart(self, timeout=None):
        """Restarts this Splunk instance.

        The service is unavailable until it has successfully restarted.

        If a *timeout* value is specified, ``restart`` blocks until the service
        resumes or the timeout period has been exceeded. Otherwise, ``restart`` returns
        immediately.

        :param timeout: A timeout period, in seconds.
        :type timeout: ``integer``
        """
        msg = {"value": "Restart requested by " + self.username + "via the Splunk SDK for Python"}
        # This message will be deleted once the server actually restarts.
        self.messages.create(name="restart_required", **msg)
        result = self.post("/services/server/control/restart")
        if timeout is None:
            return result
        start = datetime.now()
        diff = timedelta(seconds=timeout)
        while datetime.now() - start < diff:
            try:
                self.login()
                if not self.restart_required:
                    return result
            except Exception as e:
                sleep(1)
        raise Exception("Operation time out.")

    @property
    def restart_required(self):
        """Indicates whether splunkd is in a state that requires a restart.

        :return: A ``boolean`` that indicates whether a restart is required.

        """
        response = self.get("messages").body.read()
        messages = load(response)['feed']
        if 'entry' not in messages:
            result = False
        else:
            if isinstance(messages['entry'], dict):
                titles = [messages['entry']['title']]
            else:
                titles = [x['title'] for x in messages['entry']]
            result = 'restart_required' in titles
        return result

    @property
    def roles(self):
        """Returns the collection of user roles.

        :return: A :class:`Roles` collection of :class:`Role` entities.
        """
        return Roles(self)

    def search(self, query, **kwargs):
        """Runs a search using a search query and any optional arguments you
        provide, and returns a `Job` object representing the search.

        :param query: A search query.
        :type query: ``string``
        :param kwargs: Arguments for the search (optional):

            * "output_mode" (``string``): Specifies the output format of the
              results.

            * "earliest_time" (``string``): Specifies the earliest time in the
              time range to
              search. The time string can be a UTC time (with fractional
              seconds), a relative time specifier (to now), or a formatted
              time string.

            * "latest_time" (``string``): Specifies the latest time in the time
              range to
              search. The time string can be a UTC time (with fractional
              seconds), a relative time specifier (to now), or a formatted
              time string.

            * "rf" (``string``): Specifies one or more fields to add to the
              search.

        :type kwargs: ``dict``
        :rtype: class:`Job`
        :returns: An object representing the created job.
        """
        return self.jobs.create(query, **kwargs)

    @property
    def saved_searches(self):
        """Returns the collection of saved searches.

        :return: A :class:`SavedSearches` collection of :class:`SavedSearch`
            entities.
        """
        return SavedSearches(self)

    @property
    def settings(self):
        """Returns the configuration settings for this instance of Splunk.

        :return: A :class:`Settings` object containing configuration settings.
        """
        return Settings(self)

    @property
    def splunk_version(self):
        """Returns the version of the splunkd instance this object is attached
        to.

        The version is returned as a tuple of the version components as
        integers (for example, `(4,3,3)` or `(5,)`).

        :return: A ``tuple`` of ``integers``.
        """
        if self._splunk_version is None:
            self._splunk_version = tuple(int(p) for p in self.info['version'].split('.'))
        return self._splunk_version

    @property
    def splunk_instance(self):
        if self._instance_type is None:
            splunk_info = self.info;
            if hasattr(splunk_info, 'instance_type'):
                self._instance_type = splunk_info['instance_type']
            else:
                self._instance_type = ''
        return self._instance_type

    @property
    def disable_v2_api(self):
        if self.splunk_instance.lower() == 'cloud':
            return self.splunk_version < (9, 0, 2209)
        return self.splunk_version < (9, 0, 2)

    @property
    def kvstore_owner(self):
        """Returns the KVStore owner for this instance of Splunk.

        By default is the kvstore owner is not set, it will return "nobody"
        :return: A string with the KVStore owner.
        """
        if self._kvstore_owner is None:
            self._kvstore_owner = "nobody"
        return self._kvstore_owner

    @kvstore_owner.setter
    def kvstore_owner(self, value):
        """
        kvstore is refreshed, when the owner value is changed
        """
        self._kvstore_owner = value
        self.kvstore

    @property
    def kvstore(self):
        """Returns the collection of KV Store collections.

        sets the owner for the namespace, before retrieving the KVStore Collection

        :return: A :class:`KVStoreCollections` collection of :class:`KVStoreCollection` entities.
        """
        self.namespace['owner'] = self.kvstore_owner
        return KVStoreCollections(self)

    @property
    def users(self):
        """Returns the collection of users.

        :return: A :class:`Users` collection of :class:`User` entities.
        """
        return Users(self)
