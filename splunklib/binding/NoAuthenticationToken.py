# Singleton values to eschew None
class _NoAuthenticationToken:
    """The value stored in a :class:`Context` or :class:`splunklib.client.Service`
    class that is not logged in.

    If a ``Context`` or ``Service`` object is created without an authentication
    token, and there has not yet been a call to the ``login`` method, the token
    field of the ``Context`` or ``Service`` object is set to
    ``_NoAuthenticationToken``.

    Likewise, after a ``Context`` or ``Service`` object has been logged out, the
    token is set to this value again.
    """