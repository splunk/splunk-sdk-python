from .Entity import Entity


class User(Entity):
    """This class represents a Splunk user.
    """

    @property
    def role_entities(self):
        """Returns a list of roles assigned to this user.

        :return: The list of roles.
        :rtype: ``list``
        """
        return [self.service.roles[name] for name in self.content.roles]
