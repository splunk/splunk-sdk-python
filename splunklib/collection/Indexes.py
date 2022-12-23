from .Collection import Collection

from splunklib.exceptions import IllegalOperationException


class Indexes(Collection):
    """This class contains the collection of indexes in this Splunk instance.
    Retrieve this collection using :meth:`Service.indexes`.
    """

    def get_default(self):
        """ Returns the name of the default index.

        :return: The name of the default index.

        """
        index = self['_audit']
        return index['defaultDatabase']

    def delete(self, name):
        """ Deletes a given index.

        **Note**: This method is only supported in Splunk 5.0 and later.

        :param name: The name of the index to delete.
        :type name: ``string``
        """
        if self.service.splunk_version >= (5,):
            Collection.delete(self, name)
        else:
            raise IllegalOperationException("Deleting indexes via the REST API is "
                                            "not supported before Splunk version 5.")
