# Splunk automatically lowercases new user names so we need to match that
# behavior here to ensure that the subsequent member lookup works correctly.
from urllib import parse

from .Collection import Collection

from splunklib.entity import User
from splunklib.client.utils import _load_atom, _parse_atom_entry
from splunklib.constants import PATH_USERS, XNAME_ENTRY


class Users(Collection):
    """This class represents the collection of Splunk users for this instance of
    Splunk. Retrieve this collection using :meth:`Service.users`.
    """

    def __init__(self, service):
        Collection.__init__(self, service, PATH_USERS, item=User)

    def __getitem__(self, key):
        return Collection.__getitem__(self, key.lower())

    def __contains__(self, name):
        return Collection.__contains__(self, name.lower())

    def create(self, username, password, roles, **params):
        """Creates a new user.

        This function makes two roundtrips to the server, plus at most
        two more if
        the ``autologin`` field of :func:`connect` is set to ``True``.

        :param username: The username.
        :type username: ``string``
        :param password: The password.
        :type password: ``string``
        :param roles: A single role or list of roles for the user.
        :type roles: ``string`` or  ``list``
        :param params: Additional arguments (optional). For a list of available
            parameters, see `User authentication parameters
            <http://dev.splunk.com/view/SP-CAAAEJ6#userauthparams>`_
            on Splunk Developer Portal.
        :type params: ``dict``

        :return: The new user.
        :rtype: :class:`User`

        **Example**::

            import splunklib.client as client
            c = client.connect(...)
            users = c.users
            boris = users.create("boris", "securepassword", roles="user")
            hilda = users.create("hilda", "anotherpassword", roles=["user","power"])
        """
        if not isinstance(username, str):
            raise ValueError(f"Invalid username: {str(username)}")
        username = username.lower()
        self.post(name=username, password=password, roles=roles, **params)
        # splunkd doesn't return the user in the POST response body,
        # so we have to make a second round trip to fetch it.
        response = self.get(username)
        entry = _load_atom(response, XNAME_ENTRY).entry
        state = _parse_atom_entry(entry)
        entity = self.item(
            self.service,
            parse.unquote(state.links.alternate),
            state=state)
        return entity

    def delete(self, name):
        """ Deletes the user and returns the resulting collection of users.

        :param name: The name of the user to delete.
        :type name: ``string``

        :return:
        :rtype: :class:`Users`
        """
        return Collection.delete(self, name.lower())
