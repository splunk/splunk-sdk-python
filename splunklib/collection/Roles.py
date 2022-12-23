from urllib import parse

from .Collection import Collection
from splunklib.entity import Role

from splunklib.client.utils import _load_atom, _parse_atom_entry
from splunklib.constants import PATH_ROLES, XNAME_ENTRY


class Roles(Collection):
    """This class represents the collection of roles in the Splunk instance.
    Retrieve this collection using :meth:`Service.roles`."""

    def __init__(self, service):
        return Collection.__init__(self, service, PATH_ROLES, item=Role)

    def __getitem__(self, key):
        return Collection.__getitem__(self, key.lower())

    def __contains__(self, name):
        return Collection.__contains__(self, name.lower())

    def create(self, name, **params):
        """Creates a new role.

        This function makes two roundtrips to the server, plus at most
        two more if
        the ``autologin`` field of :func:`connect` is set to ``True``.

        :param name: Name for the role.
        :type name: ``string``
        :param params: Additional arguments (optional). For a list of available
            parameters, see `Roles parameters
            <http://dev.splunk.com/view/SP-CAAAEJ6#rolesparams>`_
            on Splunk Developer Portal.
        :type params: ``dict``

        :return: The new role.
        :rtype: :class:`Role`

        **Example**::

            import splunklib.client as client
            c = client.connect(...)
            roles = c.roles
            paltry = roles.create("paltry", imported_roles="user", defaultApp="search")
        """
        if not isinstance(name, str):
            raise ValueError(f"Invalid role name: {str(name)}")
        name = name.lower()
        self.post(name=name, **params)
        # splunkd doesn't return the user in the POST response body,
        # so we have to make a second round trip to fetch it.
        response = self.get(name)
        entry = _load_atom(response, XNAME_ENTRY).entry
        state = _parse_atom_entry(entry)
        entity = self.item(
            self.service,
            parse.unquote(state.links.alternate),
            state=state)
        return entity

    def delete(self, name):
        """ Deletes the role and returns the resulting collection of roles.

        :param name: The name of the role to delete.
        :type name: ``string``

        :rtype: The :class:`Roles`
        """
        return Collection.delete(self, name.lower())
