from .Entity import Entity
from splunklib.exceptions import NoSuchCapability


class Role(Entity):
    """This class represents a user role.
    """

    def grant(self, *capabilities_to_grant):
        """Grants additional capabilities to this role.

        :param capabilities_to_grant: Zero or more capabilities to grant this
            role. For a list of capabilities, see
            `Capabilities <http://dev.splunk.com/view/SP-CAAAEJ6#capabilities>`_
            on Splunk Developer Portal.
        :type capabilities_to_grant: ``string`` or ``list``
        :return: The :class:`Role`.

        **Example**::

            service = client.connect(...)
            role = service.roles['somerole']
            role.grant('change_own_password', 'search')
        """
        possible_capabilities = self.service.capabilities
        for capability in capabilities_to_grant:
            if capability not in possible_capabilities:
                raise NoSuchCapability(capability)
        new_capabilities = self['capabilities'] + list(capabilities_to_grant)
        self.post(capabilities=new_capabilities)
        return self

    def revoke(self, *capabilities_to_revoke):
        """Revokes zero or more capabilities from this role.

        :param capabilities_to_revoke: Zero or more capabilities to grant this
            role. For a list of capabilities, see
            `Capabilities <http://dev.splunk.com/view/SP-CAAAEJ6#capabilities>`_
            on Splunk Developer Portal.
        :type capabilities_to_revoke: ``string`` or ``list``

        :return: The :class:`Role`.

        **Example**::

            service = client.connect(...)
            role = service.roles['somerole']
            role.revoke('change_own_password', 'search')
        """
        possible_capabilities = self.service.capabilities
        for capability in capabilities_to_revoke:
            if capability not in possible_capabilities:
                raise NoSuchCapability(capability)
        old_capabilities = self['capabilities']
        new_capabilities = []
        for c in old_capabilities:
            if c not in capabilities_to_revoke:
                new_capabilities.append(c)
        if not new_capabilities:
            new_capabilities = ''  # Empty lists don't get passed in the body, so we have to force an empty argument.
        self.post(capabilities=new_capabilities)
        return self
