from .Collection import Collection

from splunklib.binding import UrlEncoded
from splunklib.entity import StoragePassword
from splunklib.client.utils import _load_atom_entries, _parse_atom_entry
from splunklib.constants import PATH_STORAGE_PASSWORDS


class StoragePasswords(Collection):
    """This class provides access to the storage passwords from this Splunk
    instance. Retrieve this collection using :meth:`Service.storage_passwords`.
    """

    def __init__(self, service):
        if service.namespace.owner == '-' or service.namespace.app == '-':
            raise ValueError("StoragePasswords cannot have wildcards in namespace.")
        super().__init__(service, PATH_STORAGE_PASSWORDS, item=StoragePassword)

    def create(self, password, username, realm=None):
        """ Creates a storage password.

        A `StoragePassword` can be identified by <username>, or by <realm>:<username> if the
        optional realm parameter is also provided.

        :param password: The password for the credentials - this is the only part of the credentials that will be stored securely.
        :type name: ``string``
        :param username: The username for the credentials.
        :type name: ``string``
        :param realm: The credential realm. (optional)
        :type name: ``string``

        :return: The :class:`StoragePassword` object created.
        """
        if not isinstance(username, str):
            raise ValueError(f"Invalid name: {repr(username)}")

        if realm is None:
            response = self.post(password=password, name=username)
        else:
            response = self.post(password=password, realm=realm, name=username)

        if response.status != 201:
            raise ValueError(f"Unexpected status code {response.status} returned from creating a stanza")

        entries = _load_atom_entries(response)
        state = _parse_atom_entry(entries[0])
        storage_password = StoragePassword(self.service, self._entity_path(state), state=state, skip_refresh=True)

        return storage_password

    def delete(self, username, realm=None):
        """Delete a storage password by username and/or realm.

        The identifier can be passed in through the username parameter as
        <username> or <realm>:<username>, but the preferred way is by
        passing in the username and realm parameters.

        :param username: The username for the credentials, or <realm>:<username> if the realm parameter is omitted.
        :type name: ``string``
        :param realm: The credential realm. (optional)
        :type name: ``string``
        :return: The `StoragePassword` collection.
        :rtype: ``self``
        """
        if self.service.namespace.owner == '-' or self.service.namespace.app == '-':
            raise ValueError("app context must be specified when removing a password.")

        if realm is None:
            # This case makes the username optional, so
            # the full name can be passed in as realm.
            # Assume it's already encoded.
            name = username
        else:
            # Encode each component separately
            name = UrlEncoded(realm, encode_slash=True) + ":" + UrlEncoded(username, encode_slash=True)

        # Append the : expected at the end of the name
        if name[-1] != ":":
            name = name + ":"
        return Collection.delete(self, name)
