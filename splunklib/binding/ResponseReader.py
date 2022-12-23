# Converts an httplib response into a file-like object.
import io


class ResponseReader(io.RawIOBase):
    """This class provides a file-like interface for :class:`httplib` responses.

    The ``ResponseReader`` class is intended to be a layer to unify the different
    types of HTTP libraries used with this SDK. This class also provides a
    preview of the stream and a few useful predicates.
    """

    # For testing, you can use a StringIO as the argument to
    # ``ResponseReader`` instead of an ``httplib.HTTPResponse``. It
    # will work equally well.
    def __init__(self, response, connection=None):
        self._response = response
        self._connection = connection
        self._buffer = b''

    def __str__(self):
        return str(self.read(), 'UTF-8')

    @property
    def empty(self):
        """Indicates whether there is any more data in the response."""
        return self.peek(1) == b""

    def peek(self, size):
        """Nondestructively retrieves a given number of characters.

        The next :meth:`read` operation behaves as though this method was never
        called.

        :param size: The number of characters to retrieve.
        :type size: ``integer``
        """
        c = self.read(size)
        self._buffer = self._buffer + c
        return c

    def close(self):
        """Closes this response."""
        if self._connection:
            self._connection.close()
        self._response.close()

    def read(self, size=None):
        """Reads a given number of characters from the response.

        :param size: The number of characters to read, or "None" to read the
            entire response.
        :type size: ``integer`` or "None"

        """
        r = self._buffer
        self._buffer = b''
        if size is not None:
            size -= len(r)
        r = r + self._response.read(size)
        return r

    def readable(self):
        """ Indicates that the response reader is readable."""
        return True

    def readinto(self, byte_array):
        """ Read data into a byte array, upto the size of the byte array.

        :param byte_array: A byte array/memory view to pour bytes into.
        :type byte_array: ``bytearray`` or ``memoryview``

        """
        max_size = len(byte_array)
        data = self.read(max_size)
        bytes_read = len(data)
        byte_array[:bytes_read] = data
        return bytes_read
