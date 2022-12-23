from .Entity import Entity


class Message(Entity):
    def __init__(self, service, path, **kwargs):
        Entity.__init__(self, service, path, **kwargs)

    @property
    def value(self):
        """Returns the message value.

        :return: The message value.
        :rtype: ``string``
        """
        return self[self.name]
