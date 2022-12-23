class Message:
    """This class represents informational messages that Splunk interleaves in the results stream.

    ``Message`` takes two arguments: a string giving the message type (e.g., "DEBUG"), and
    a string giving the message itself.

    **Example**::

        m = Message("DEBUG", "There's something in that variable...")
    """

    def __init__(self, type_, message):
        self.type = type_
        self.message = message

    def __repr__(self):
        return f"{self.type}: {self.message}"

    def __eq__(self, other):
        return (self.type, self.message) == (other.type, other.message)

    def __hash__(self):
        return hash((self.type, self.message))
