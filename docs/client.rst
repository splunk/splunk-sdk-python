splunklib.client
----------------

.. automodule:: splunklib.client

.. autofunction:: connect

.. autoclass:: Service
    :members: apps, confs, capabilities, event_types, fired_alerts, indexes, info, inputs, jobs, loggers, messages, modular_input_kinds, parse, restart, restart_required, roles, search, saved_searches, settings, splunk_version, users
    :inherited-members:

.. autoclass:: Endpoint
    :members: get, post
    :inherited-members:

.. autoclass:: Entity
    :members: delete, get, post, refresh, access, disable, enable, fields, links, name, namespace, reload, update
    :inherited-members:

.. autoclass:: ReadOnlyCollection
    :members: itemmeta, iter, list, names
    :inherited-members:

.. autoclass:: Collection
    :members: create, delete
    :inherited-members:

.. autoclass:: ConfigurationFile
    :inherited-members:

.. autoclass:: Configurations
    :members: create, delete
    :inherited-members:

.. autoclass:: Stanza
    :members: submit
    :inherited-members:

.. autoclass:: AlertGroup
    :members: alerts, count
    :inherited-members:

.. autoclass:: Indexes
    :members: default, delete
    :inherited-members:

.. autoclass:: Index
    :members: attach, attached_socket, clean, disable, enable, roll_hot_buckets, submit, upload
    :inherited-members:

.. autoclass:: Input
    :members: update
    :inherited-members:

.. autoclass:: Inputs
    :members: create, delete, itemmeta, kinds, kindpath, list, iter, oneshot
    :inherited-members:

.. autoclass:: Job
    :members: cancel, disable_preview, enable_preview, events, finalize, is_done, is_ready, name, pause, refresh, results, preview, searchlog, set_priority, summary, timeline, touch, set_ttl, unpause
    :inherited-members:

.. autoclass:: Jobs
    :members: create, export, itemmeta, oneshot
    :inherited-members:

.. autoclass:: Loggers
    :members: itemmeta
    :inherited-members:

.. autoclass:: Message
    :members: value
    :inherited-members:

.. autoclass:: ModularInputKind
    :members: arguments, update
    :inherited-members:

.. autoclass:: SavedSearch
    :members: acknowledge, alert_count, dispatch, fired_alerts, history, update, scheduled_times, suppress, suppressed, unsuppress
    :inherited-members:

.. autoclass:: SavedSearches
    :members: create
    :inherited-members:

.. autoclass:: Settings
    :members: update
    :inherited-members:

.. autoclass:: User
    :members: role_entities
    :inherited-members:

.. autoclass:: Users
    :members: create, delete
    :inherited-members:

.. autoclass:: Role
    :members: grant, revoke
    :inherited-members:

.. autoclass:: Roles
    :members: create, delete
    :inherited-members:

.. autoclass:: Application
    :members: setupInfo, package, updateInfo
    :inherited-members:

.. autoclass:: NoSuchUserException
    :members:

.. autoclass:: NoSuchApplicationException
    :members:

.. autoclass:: IllegalOperationException
    :members:

.. autoclass:: IncomparableException
    :members:

.. autoclass:: JobNotReadyException
    :members:

.. autoclass:: AmbiguousReferenceException
    :members:

.. autoclass:: EntityDeletedException
    :members:

.. autoclass:: InvalidNameException
    :members:

.. autoclass:: OperationFailedException
    :members:

.. autoclass:: NoSuchCapability
    :members:

.. autoclass:: OperationError
    :members:

.. autoclass:: NotSupportedError
    :members:
