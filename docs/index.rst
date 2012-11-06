Welcome to the API reference for the Splunk Python SDK, which describes the modules that are included in the Splunk Python SDK.
For more information about the SDK, see the `Splunk Developer Portal <http://dev.splunk.com/view/python-sdk/SP-CAAAEBB>`_.

.. toctree::
   :maxdepth: 2

:doc:`binding`
--------------

    :func:`~splunklib.binding.connect` function

    :func:`~splunklib.binding.namespace` function

    :class:`~splunklib.binding.Context` class

    :class:`~splunklib.binding.ResponseReader` class

    :class:`~splunklib.binding.UrlEncoded` class


    **Exceptions**

    :func:`~splunklib.binding.handler` function

    :class:`~splunklib.binding.AuthenticationError` class

    :class:`~splunklib.binding.NoAuthenticationToken` class

    **Custom HTTP handler**

    :class:`~splunklib.binding.HTTPError` class 

    :class:`~splunklib.binding.HttpLib` class


:doc:`client`
-------------

    :func:`~splunklib.client.connect` function

    :class:`~splunklib.client.Service` class 

    :class:`~splunklib.client.Endpoint` base class 


    **Entities and collections**

    :class:`~splunklib.client.Entity` class

    :class:`~splunklib.client.Collection` class

    :class:`~splunklib.client.ReadOnlyCollection` class

    :class:`~splunklib.client.Application` class

    :class:`~splunklib.client.AlertGroup` class

    :class:`~splunklib.client.ConfigurationFile` class

    :class:`~splunklib.client.Stanza` class

    :class:`~splunklib.client.Configurations` class

    :class:`~splunklib.client.Index` class

    :class:`~splunklib.client.Indexes` class

    :class:`~splunklib.client.Input` class

    :class:`~splunklib.client.Inputs` class

    :class:`~splunklib.client.Job` class

    :class:`~splunklib.client.Jobs` class

    :class:`~splunklib.client.Loggers` class

    :class:`~splunklib.client.Message` class

    :class:`~splunklib.client.ModularInputKind` class

    :class:`~splunklib.client.Role` class

    :class:`~splunklib.client.Roles` class

    :class:`~splunklib.client.SavedSearch` class

    :class:`~splunklib.client.SavedSearches` class

    :class:`~splunklib.client.Settings` class

    :class:`~splunklib.client.User` class

    :class:`~splunklib.client.Users` class
    

    **Exceptions**

    :class:`~splunklib.client.AmbiguousReferenceException` class

    :class:`~splunklib.client.EntityDeletedException` class

    :class:`~splunklib.client.IllegalOperationException` class

    :class:`~splunklib.client.IncomparableException` class

    :class:`~splunklib.client.InvalidNameException` class

    :class:`~splunklib.client.JobNotReadyException` class

    :class:`~splunklib.client.NoSuchApplicationException` class

    :class:`~splunklib.client.NoSuchCapability` class

    :class:`~splunklib.client.NoSuchUserException` class

    :class:`~splunklib.client.NotSupportedError` class

    :class:`~splunklib.client.OperationError` class

    :class:`~splunklib.client.OperationFailedException` class
    

:doc:`data`
-----------

    :func:`~splunklib.data.load` function

    :func:`~splunklib.data.record` function

    :class:`~splunklib.data.Record` class 

:doc:`results`
--------------

    :class:`~splunklib.results.ResultsReader` class 

    :class:`~splunklib.results.Message` class 
