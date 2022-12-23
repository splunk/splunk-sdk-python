from .Entity import Entity

from splunklib import collection


class AlertGroup(Entity):
    """This class represents a group of fired alerts for a saved search. Access
    it using the :meth:`alerts` property."""

    def __init__(self, service, path, **kwargs):
        Entity.__init__(self, service, path, **kwargs)

    def __len__(self):
        return self.count

    @property
    def alerts(self):
        """Returns a collection of triggered alerts.

        :return: A :class:`Collection` of triggered alerts.
        """
        return collection.Collection(self.service, self.path)

    @property
    def count(self):
        """Returns the count of triggered alerts.

        :return: The triggered alert count.
        :rtype: ``integer``
        """
        return int(self.content.get('triggered_alert_count', 0))
