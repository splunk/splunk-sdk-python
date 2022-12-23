# In preparation for adding Storm support, we added an
# intermediary class between Service and Context. Storm's
# API is not going to be the same as enterprise Splunk's
# API, so we will derive both Service (for enterprise Splunk)
# and StormService for (Splunk Storm) from _BaseService, and
# put any shared behavior on it.
from splunklib.binding import Context


class _BaseService(Context):
    pass
