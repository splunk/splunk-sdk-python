class IncomparableException(Exception):
    """Thrown when trying to compare objects (using ``==``, ``<``, ``>``, and
    so on) of a type that doesn't support it."""
