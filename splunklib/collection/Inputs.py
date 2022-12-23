# Inputs is a "kinded" collection, which is a heterogenous collection where
# each item is tagged with a kind, that provides a single merged view of all
# input kinds.
import logging
from urllib import parse

from .Collection import Collection

from splunklib.binding import UrlEncoded
from splunklib.entity import Input
from splunklib.exceptions import AmbiguousReferenceException, HTTPError

from splunklib.client.utils import _load_atom, _load_atom_entries, _path, _parse_atom_entry, _parse_atom_metadata
from splunklib.constants import PATH_INPUTS, MATCH_ENTRY_CONTENT

logger = logging.getLogger(__name__)


class Inputs(Collection):
    """This class represents a collection of inputs. The collection is
    heterogeneous and each member of the collection contains a *kind* property
    that indicates the specific type of input.
    Retrieve this collection using :meth:`Service.inputs`."""

    def __init__(self, service, kindmap=None):
        Collection.__init__(self, service, PATH_INPUTS, item=Input)

    def __getitem__(self, key):
        # The key needed to retrieve the input needs it's parenthesis to be URL encoded
        # based on the REST API for input
        # <http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTinput>
        if isinstance(key, tuple) and len(key) == 2:
            # Fetch a single kind
            key, kind = key
            key = UrlEncoded(key, encode_slash=True)
            try:
                response = self.get(self.kindpath(kind) + "/" + key)
                entries = self._load_list(response)
                if len(entries) > 1:
                    raise AmbiguousReferenceException(f"Found multiple inputs of kind {kind} named {key}.")
                if len(entries) == 0:
                    raise KeyError((key, kind))
                return entries[0]
            except HTTPError as he:
                if he.status == 404:  # No entity matching kind and key
                    raise KeyError((key, kind))
                else:
                    raise
        else:
            # Iterate over all the kinds looking for matches.
            kind = None
            candidate = None
            key = UrlEncoded(key, encode_slash=True)
            for kind in self.kinds:
                try:
                    response = self.get(kind + "/" + key)
                    entries = self._load_list(response)
                    if len(entries) > 1:
                        raise AmbiguousReferenceException(f"Found multiple inputs of kind {kind} named {key}.")
                    if len(entries) == 0:
                        pass
                    if candidate is not None:  # Already found at least one candidate
                        raise AmbiguousReferenceException(
                            f"Found multiple inputs named {key}, please specify a kind")
                    candidate = entries[0]
                except HTTPError as he:
                    if he.status == 404:
                        pass  # Just carry on to the next kind.
                    else:
                        raise
            if candidate is None:
                raise KeyError(key)  # Never found a match.
            return candidate

    def __contains__(self, key):
        if isinstance(key, tuple) and len(key) == 2:
            # If we specify a kind, this will shortcut properly
            try:
                self.__getitem__(key)
                return True
            except KeyError:
                return False
        else:
            # Without a kind, we want to minimize the number of round trips to the server, so we
            # reimplement some of the behavior of __getitem__ in order to be able to stop searching
            # on the first hit.
            for kind in self.kinds:
                try:
                    response = self.get(self.kindpath(kind) + "/" + key)
                    entries = self._load_list(response)
                    if len(entries) > 0:
                        return True
                    pass
                except HTTPError as he:
                    if he.status == 404:
                        pass  # Just carry on to the next kind.
                    else:
                        raise
            return False

    def create(self, name, kind, **kwargs):
        """Creates an input of a specific kind in this collection, with any
        arguments you specify.

        :param `name`: The input name.
        :type name: ``string``
        :param `kind`: The kind of input:

            - "ad": Active Directory

            - "monitor": Files and directories

            - "registry": Windows Registry

            - "script": Scripts

            - "splunktcp": TCP, processed

            - "tcp": TCP, unprocessed

            - "udp": UDP

            - "win-event-log-collections": Windows event log

            - "win-perfmon": Performance monitoring

            - "win-wmi-collections": WMI

        :type kind: ``string``
        :param `kwargs`: Additional arguments (optional). For more about the
            available parameters, see `Input parameters <http://dev.splunk.com/view/SP-CAAAEE6#inputparams>`_ on Splunk Developer Portal.

        :type kwargs: ``dict``

        :return: The new :class:`Input`.
        """
        kindpath = self.kindpath(kind)
        self.post(kindpath, name=name, **kwargs)

        # If we created an input with restrictToHost set, then
        # its path will be <restrictToHost>:<name>, not just <name>,
        # and we have to adjust accordingly.

        # Url encodes the name of the entity.
        name = UrlEncoded(name, encode_slash=True)
        path = _path(
            self.path + kindpath,
            f"{kwargs['restrictToHost']}:{name}" if 'restrictToHost' in kwargs else name
        )
        return Input(self.service, path, kind)

    def delete(self, name, kind=None):
        """Removes an input from the collection.

        :param `kind`: The kind of input:

            - "ad": Active Directory

            - "monitor": Files and directories

            - "registry": Windows Registry

            - "script": Scripts

            - "splunktcp": TCP, processed

            - "tcp": TCP, unprocessed

            - "udp": UDP

            - "win-event-log-collections": Windows event log

            - "win-perfmon": Performance monitoring

            - "win-wmi-collections": WMI

        :type kind: ``string``
        :param name: The name of the input to remove.
        :type name: ``string``

        :return: The :class:`Inputs` collection.
        """
        if kind is None:
            self.service.delete(self[name].path)
        else:
            self.service.delete(self[name, kind].path)
        return self

    def itemmeta(self, kind):
        """Returns metadata for the members of a given kind.

        :param `kind`: The kind of input:

            - "ad": Active Directory

            - "monitor": Files and directories

            - "registry": Windows Registry

            - "script": Scripts

            - "splunktcp": TCP, processed

            - "tcp": TCP, unprocessed

            - "udp": UDP

            - "win-event-log-collections": Windows event log

            - "win-perfmon": Performance monitoring

            - "win-wmi-collections": WMI

        :type kind: ``string``

        :return: The metadata.
        :rtype: class:``splunklib.data.Record``
        """
        response = self.get(f"{self._kindmap[kind]}/_new")
        content = _load_atom(response, MATCH_ENTRY_CONTENT)
        return _parse_atom_metadata(content)

    def _get_kind_list(self, subpath=None):
        if subpath is None:
            subpath = []

        kinds = []
        response = self.get('/'.join(subpath))
        content = _load_atom_entries(response)
        for entry in content:
            this_subpath = subpath + [entry.title]
            # The "all" endpoint doesn't work yet.
            # The "tcp/ssl" endpoint is not a real input collection.
            if entry.title == 'all' or this_subpath == ['tcp', 'ssl']:
                continue
            if 'create' in [x.rel for x in entry.link]:
                path = '/'.join(subpath + [entry.title])
                kinds.append(path)
            else:
                subkinds = self._get_kind_list(subpath + [entry.title])
                kinds.extend(subkinds)
        return kinds

    @property
    def kinds(self):
        """Returns the input kinds on this Splunk instance.

        :return: The list of input kinds.
        :rtype: ``list``
        """
        return self._get_kind_list()

    def kindpath(self, kind):
        """Returns a path to the resources for a given input kind.

        :param `kind`: The kind of input:

            - "ad": Active Directory

            - "monitor": Files and directories

            - "registry": Windows Registry

            - "script": Scripts

            - "splunktcp": TCP, processed

            - "tcp": TCP, unprocessed

            - "udp": UDP

            - "win-event-log-collections": Windows event log

            - "win-perfmon": Performance monitoring

            - "win-wmi-collections": WMI

        :type kind: ``string``

        :return: The relative endpoint path.
        :rtype: ``string``
        """
        if kind == 'tcp':
            return UrlEncoded('tcp/raw', skip_encode=True)
        if kind == 'splunktcp':
            return UrlEncoded('tcp/cooked', skip_encode=True)
        return UrlEncoded(kind, skip_encode=True)

    def list(self, *kinds, **kwargs):
        """Returns a list of inputs that are in the :class:`Inputs` collection.
        You can also filter by one or more input kinds.

        This function iterates over all possible inputs, regardless of any arguments you
        specify. Because the :class:`Inputs` collection is the union of all the inputs of each
        kind, this method implements parameters such as "count", "search", and so
        on at the Python level once all the data has been fetched. The exception
        is when you specify a single input kind, and then this method makes a single request
        with the usual semantics for parameters.

        :param kinds: The input kinds to return (optional).

            - "ad": Active Directory

            - "monitor": Files and directories

            - "registry": Windows Registry

            - "script": Scripts

            - "splunktcp": TCP, processed

            - "tcp": TCP, unprocessed

            - "udp": UDP

            - "win-event-log-collections": Windows event log

            - "win-perfmon": Performance monitoring

            - "win-wmi-collections": WMI

        :type kinds: ``string``
        :param kwargs: Additional arguments (optional):

            - "count" (``integer``): The maximum number of items to return.

            - "offset" (``integer``): The offset of the first item to return.

            - "search" (``string``): The search query to filter responses.

            - "sort_dir" (``string``): The direction to sort returned items:
              "asc" or "desc".

            - "sort_key" (``string``): The field to use for sorting (optional).

            - "sort_mode" (``string``): The collating sequence for sorting
              returned items: "auto", "alpha", "alpha_case", or "num".

        :type kwargs: ``dict``

        :return: A list of input kinds.
        :rtype: ``list``
        """
        if len(kinds) == 0:
            kinds = self.kinds
        if len(kinds) == 1:
            kind = kinds[0]
            logger.debug("Inputs.list taking short circuit branch for single kind.")
            path = self.kindpath(kind)
            logger.debug("Path for inputs: %s", path)
            try:
                path = UrlEncoded(path, skip_encode=True)
                response = self.get(path, **kwargs)
            except HTTPError as he:
                if he.status == 404:  # No inputs of this kind
                    return []
            entities = []
            entries = _load_atom_entries(response)
            if entries is None:
                return []  # No inputs in a collection comes back with no feed or entry in the XML
            for entry in entries:
                state = _parse_atom_entry(entry)
                # Unquote the URL, since all URL encoded in the SDK
                # should be of type UrlEncoded, and all str should not
                # be URL encoded.
                path = parse.unquote(state.links.alternate)
                entity = Input(self.service, path, kind, state=state)
                entities.append(entity)
            return entities

        search = kwargs.get('search', '*')

        entities = []
        for kind in kinds:
            response = None
            try:
                kind = UrlEncoded(kind, skip_encode=True)
                response = self.get(self.kindpath(kind), search=search)
            except HTTPError as e:
                if e.status == 404:
                    continue  # No inputs of this kind
                else:
                    raise

            entries = _load_atom_entries(response)
            if entries is None: continue  # No inputs to process
            for entry in entries:
                state = _parse_atom_entry(entry)
                # Unquote the URL, since all URL encoded in the SDK
                # should be of type UrlEncoded, and all str should not
                # be URL encoded.
                path = parse.unquote(state.links.alternate)
                entity = Input(self.service, path, kind, state=state)
                entities.append(entity)
        if 'offset' in kwargs:
            entities = entities[kwargs['offset']:]
        if 'count' in kwargs:
            entities = entities[:kwargs['count']]
        if kwargs.get('sort_mode', None) == 'alpha':
            sort_field = kwargs.get('sort_field', 'name')
            if sort_field == 'name':
                f = lambda x: x.name.lower()
            else:
                f = lambda x: x[sort_field].lower()
            entities = sorted(entities, key=f)
        if kwargs.get('sort_mode', None) == 'alpha_case':
            sort_field = kwargs.get('sort_field', 'name')
            if sort_field == 'name':
                f = lambda x: x.name
            else:
                f = lambda x: x[sort_field]
            entities = sorted(entities, key=f)
        if kwargs.get('sort_dir', 'asc') == 'desc':
            entities = list(reversed(entities))
        return entities

    def __iter__(self, **kwargs):
        for item in self.iter(**kwargs):
            yield item

    def iter(self, **kwargs):
        """ Iterates over the collection of inputs.

        :param kwargs: Additional arguments (optional):

            - "count" (``integer``): The maximum number of items to return.

            - "offset" (``integer``): The offset of the first item to return.

            - "search" (``string``): The search query to filter responses.

            - "sort_dir" (``string``): The direction to sort returned items:
              "asc" or "desc".

            - "sort_key" (``string``): The field to use for sorting (optional).

            - "sort_mode" (``string``): The collating sequence for sorting
              returned items: "auto", "alpha", "alpha_case", or "num".

        :type kwargs: ``dict``
        """
        for item in self.list(**kwargs):
            yield item

    def oneshot(self, path, **kwargs):
        """ Creates a oneshot data input, which is an upload of a single file
        for one-time indexing.

        :param path: The path and filename.
        :type path: ``string``
        :param kwargs: Additional arguments (optional). For more about the
            available parameters, see `Input parameters <http://dev.splunk.com/view/SP-CAAAEE6#inputparams>`_ on Splunk Developer Portal.
        :type kwargs: ``dict``
        """
        self.post('oneshot', name=path, **kwargs)
