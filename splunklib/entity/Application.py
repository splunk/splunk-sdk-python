from .Entity import Entity


class Application(Entity):
    """Represents a locally-installed Splunk app."""

    @property
    def setupInfo(self):
        """Returns the setup information for the app.

        :return: The setup information.
        """
        return self.content.get('eai:setup', None)

    def package(self):
        """ Creates a compressed package of the app for archiving."""
        return self._run_action("package")

    def updateInfo(self):
        """Returns any update information that is available for the app."""
        return self._run_action("update")
