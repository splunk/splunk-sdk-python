from .Entity import Entity


class StoragePassword(Entity):
    """This class contains a storage password.
    """

    def __init__(self, service, path, **kwargs):
        state = kwargs.get('state', None)
        kwargs['skip_refresh'] = kwargs.get('skip_refresh', state is not None)
        super().__init__(service, path, **kwargs)
        self._state = state

    @property
    def clear_password(self):
        return self.content.get('clear_password')

    @property
    def encrypted_password(self):
        return self.content.get('encr_password')

    @property
    def realm(self):
        return self.content.get('realm')

    @property
    def username(self):
        return self.content.get('username')
