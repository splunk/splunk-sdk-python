Welcome to the API reference for the Splunk SDK for Python, which describes the modules that are included in the SDK.
For more information, see the `Splunk Developer Portal <http://dev.splunk.com/view/python-sdk/SP-CAAAEBB>`_.

.. toctree::
   :maxdepth: 2

:doc:`binding`
--------------

    :func:`~splunklib.binding.connect` function

    :func:`~splunklib.binding.namespace` function

    :class:`~splunklib.binding.Context` class

    :class:`~splunklib.binding.ResponseReader` class


    **Exceptions**

    :func:`~splunklib.binding.handler` function

    :class:`~splunklib.binding.AuthenticationError` class

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

    :class:`~splunklib.client.StoragePassword` class

    :class:`~splunklib.client.StoragePasswords` class

    :class:`~splunklib.client.User` class

    :class:`~splunklib.client.Users` class


    **Exceptions**

    :class:`~splunklib.client.AmbiguousReferenceException` class

    :class:`~splunklib.client.IllegalOperationException` class

    :class:`~splunklib.client.IncomparableException` class

    :class:`~splunklib.client.InvalidNameException` class

    :class:`~splunklib.client.NoSuchCapability` class

    :class:`~splunklib.client.NotSupportedError` class

    :class:`~splunklib.client.OperationError` class


:doc:`data`
-----------

    :func:`~splunklib.data.load` function

    :func:`~splunklib.data.record` function

    :class:`~splunklib.data.Record` class

:doc:`results`
--------------

    :class:`~splunklib.results.ResultsReader` class

    :class:`~splunklib.results.Message` class

:doc:`modularinput`
-------------------

    :class:`~splunklib.modularinput.Argument` class

    :class:`~splunklib.modularinput.Event` class

    :class:`~splunklib.modularinput.EventWriter` class

    :class:`~splunklib.modularinput.InputDefinition` class

    :class:`~splunklib.modularinput.Scheme` class

    :class:`~splunklib.modularinput.Script` class

    :class:`~splunklib.modularinput.ValidationDefinition` class

:doc:`searchcommands`
---------------------

    :class:`~splunklib.searchcommands.GeneratingCommand` class

    :class:`~splunklib.searchcommands.ReportingCommand` class

    :class:`~splunklib.searchcommands.StreamingCommand` class

    :class:`~splunklib.searchcommands.Option` class
