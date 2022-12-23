from .Entity import Entity
from splunklib.exceptions import IllegalOperationException


class ModularInputKind(Entity):
    """This class contains the different types of modular inputs. Retrieve this
    collection using :meth:`Service.modular_input_kinds`.
    """

    def __contains__(self, name):
        args = self.state.content['endpoints']['args']
        if name in args:
            return True
        return Entity.__contains__(self, name)

    def __getitem__(self, name):
        args = self.state.content['endpoint']['args']
        if name in args:
            return args['item']
        return Entity.__getitem__(self, name)

    @property
    def arguments(self):
        """A dictionary of all the arguments supported by this modular input kind.

        The keys in the dictionary are the names of the arguments. The values are
        another dictionary giving the metadata about that argument. The possible
        keys in that dictionary are ``"title"``, ``"description"``, ``"required_on_create``",
        ``"required_on_edit"``, ``"data_type"``. Each value is a string. It should be one
        of ``"true"`` or ``"false"`` for ``"required_on_create"`` and ``"required_on_edit"``,
        and one of ``"boolean"``, ``"string"``, or ``"number``" for ``"data_type"``.

        :return: A dictionary describing the arguments this modular input kind takes.
        :rtype: ``dict``
        """
        return self.state.content['endpoint']['args']

    def update(self, **kwargs):
        """Raises an error. Modular input kinds are read only."""
        raise IllegalOperationException("Modular input kinds cannot be updated via the REST API.")
