from .Entity import Entity


class Settings(Entity):
    """This class represents configuration settings for a Splunk service.
    Retrieve this collection using :meth:`Service.settings`."""

    def __init__(self, service, **kwargs):
        Entity.__init__(self, service, "/services/server/settings", **kwargs)

    # Updates on the settings endpoint are POSTed to server/settings/settings.
    def update(self, **kwargs):
        """Updates the settings on the server using the arguments you provide.

        :param kwargs: Additional arguments. For a list of valid arguments, see
            `POST server/settings/{name}
            <http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTsystem#POST_server.2Fsettings.2F.7Bname.7D>`_
            in the REST API documentation.
        :type kwargs: ``dict``
        :return: The :class:`Settings` collection.
        """
        self.service.post("/services/server/settings/settings", **kwargs)
        return self
