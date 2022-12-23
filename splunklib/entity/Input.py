from .Entity import Entity
from splunklib.exceptions import IllegalOperationException


class Input(Entity):
    """This class represents a Splunk input. This class is the base for all
    typed input classes and is also used when the client does not recognize an
    input kind.
    """

    def __init__(self, service, path, kind=None, **kwargs):
        # kind can be omitted (in which case it is inferred from the path)
        # Otherwise, valid values are the paths from data/inputs ("udp",
        # "monitor", "tcp/raw"), or two special cases: "tcp" (which is "tcp/raw")
        # and "splunktcp" (which is "tcp/cooked").
        Entity.__init__(self, service, path, **kwargs)
        if kind is None:
            path_segments = path.split('/')
            i = path_segments.index('inputs') + 1
            if path_segments[i] == 'tcp':
                self.kind = path_segments[i] + '/' + path_segments[i + 1]
            else:
                self.kind = path_segments[i]
        else:
            self.kind = kind

        # Handle old input kind names.
        if self.kind == 'tcp':
            self.kind = 'tcp/raw'
        if self.kind == 'splunktcp':
            self.kind = 'tcp/cooked'

    def update(self, **kwargs):
        """Updates the server with any changes you've made to the current input
        along with any additional arguments you specify.

        :param kwargs: Additional arguments (optional). For more about the available parameters, see `Input
        parameters <http://dev.splunk.com/view/SP-CAAAEE6#inputparams>`_ on Splunk Developer Portal.
        :type kwargs: ``dict``

        :return: The input this method was called on.
        :rtype: class:`Input`
        """
        # UDP and TCP inputs require special handling due to their restrictToHost
        # field. For all other inputs kinds, we can dispatch to the superclass method.
        if self.kind not in ['tcp', 'splunktcp', 'tcp/raw', 'tcp/cooked', 'udp']:
            return super().update(**kwargs)
        else:
            # The behavior of restrictToHost is inconsistent across input kinds and versions of Splunk.
            # In Splunk 4.x, the name of the entity is only the port, independent of the value of
            # restrictToHost. In Splunk 5.0 this changed so the name will be of the form <restrictToHost>:<port>.
            # In 5.0 and 5.0.1, if you don't supply the restrictToHost value on every update, it will
            # remove the host restriction from the input. As of 5.0.2 you simply can't change restrictToHost
            # on an existing input.

            # The logic to handle all these cases:
            # - Throw an exception if the user tries to set restrictToHost on an existing input
            #   for *any* version of Splunk.
            # - Set the existing restrictToHost value on the update args internally so we don't
            #   cause it to change in Splunk 5.0 and 5.0.1.
            to_update = kwargs.copy()

            if 'restrictToHost' in kwargs:
                raise IllegalOperationException("Cannot set restrictToHost on an existing input with the SDK.")
            if 'restrictToHost' in self._state.content and self.kind != 'udp':
                to_update['restrictToHost'] = self._state.content['restrictToHost']

            # Do the actual update operation.
            return super().update(**to_update)
