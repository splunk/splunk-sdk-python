import urllib


class UrlEncoded(str):
    """This class marks URL-encoded strings.
    It should be considered an SDK-private implementation detail.

    Manually tracking whether strings are URL encoded can be difficult. Avoid
    calling ``urllib.quote`` to replace special characters with escapes. When
    you receive a URL-encoded string, *do* use ``urllib.unquote`` to replace
    escapes with single characters. Then, wrap any string you want to use as a
    URL in ``UrlEncoded``. Note that because the ``UrlEncoded`` class is
    idempotent, making multiple calls to it is OK.

    ``UrlEncoded`` objects are identical to ``str`` objects (including being
    equal if their contents are equal) except when passed to ``UrlEncoded``
    again.

    ``UrlEncoded`` removes the ``str`` type support for interpolating values
    with ``%`` (doing that raises a ``TypeError``). There is no reliable way to
    encode values this way, so instead, interpolate into a string, quoting by
    hand, and call ``UrlEncode`` with ``skip_encode=True``.

    **Example**::

        import urllib
        UrlEncoded(f'{scheme}://{urllib.quote(host)}', skip_encode=True)

    If you append ``str`` strings and ``UrlEncoded`` strings, the result is also
    URL encoded.

    **Example**::

        UrlEncoded('ab c') + 'de f' == UrlEncoded('ab cde f')
        'ab c' + UrlEncoded('de f') == UrlEncoded('ab cde f')
    """

    def __new__(self, val='', skip_encode=False, encode_slash=False):
        if isinstance(val, UrlEncoded):
            # Don't urllib.quote something already URL encoded.
            return val
        if skip_encode:
            return str.__new__(self, val)
        if encode_slash:
            return str.__new__(self, urllib.parse.quote_plus(val))
        # When subclassing str, just call str.__new__ method
        # with your class and the value you want to have in the
        # new string.
        return str.__new__(self, urllib.parse.quote(val))

    def __add__(self, other):
        """self + other

        If *other* is not a ``UrlEncoded``, URL encode it before
        adding it.
        """
        if isinstance(other, UrlEncoded):
            return UrlEncoded(str.__add__(self, other), skip_encode=True)

        return UrlEncoded(str.__add__(self, urllib.parse.quote(other)), skip_encode=True)

    def __radd__(self, other):
        """other + self

        If *other* is not a ``UrlEncoded``, URL _encode it before
        adding it.
        """
        if isinstance(other, UrlEncoded):
            return UrlEncoded(str.__radd__(self, other), skip_encode=True)

        return UrlEncoded(str.__add__(urllib.parse.quote(other), self), skip_encode=True)

    def __mod__(self, fields):
        """Interpolation into ``UrlEncoded``s is disabled.

        If you try to write ``UrlEncoded("%s") % "abc", will get a
        ``TypeError``.
        """
        raise TypeError("Cannot interpolate into a UrlEncoded object.")

    def __repr__(self):
        return f"UrlEncoded({repr(urllib.parse.unquote(str(self)))})"
