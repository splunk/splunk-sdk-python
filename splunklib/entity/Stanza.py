from .Entity import Entity

from splunklib.binding.utils import _encode


class Stanza(Entity):
    """This class contains a single configuration stanza."""

    def submit(self, stanza):
        """Adds keys to the current configuration stanza as a
        dictionary of key-value pairs.

        :param stanza: A dictionary of key-value pairs for the stanza.
        :type stanza: ``dict``
        :return: The :class:`Stanza` object.
        """
        body = _encode(**stanza)
        self.service.post(self.path, body=body)
        return self

    def __len__(self):
        # The stanza endpoint returns all the keys at the same level in the XML as the eai information
        # and 'disabled', so to get an accurate length, we have to filter those out and have just
        # the stanza keys.
        return len([x for x in list(self._state.content.keys())
                    if not x.startswith('eai') and x != 'disabled'])
