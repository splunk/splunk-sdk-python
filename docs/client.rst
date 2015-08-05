splunklib.client
----------------

.. automodule:: splunklib.client

.. autofunction:: connect

.. autoclass:: AmbiguousReferenceException
    :members:

.. autoclass:: Application
    :members: setupInfo, package, updateInfo
    :inherited-members:

.. autoclass:: AlertGroup
    :members: alerts, count
    :inherited-members:

.. autoclass:: Collection
    :members: create, delete
    :inherited-members:

.. autoclass:: ConfigurationFile
    :inherited-members:

.. autoclass:: Configurations
    :members: create, delete
    :inherited-members:

.. autoclass:: Endpoint
    :members: get, post
    :inherited-members:

.. autoclass:: Entity
    :members: access, delete, disable, enable, fields, get, links, name, namespace, post, refresh, reload, update
    :inherited-members:

.. autoclass:: IllegalOperationException
    :members:

.. autoclass:: IncomparableException
    :members:

.. autoclass:: Index
    :members: attach, attached_socket, clean, disable, enable, roll_hot_buckets, submit, upload
    :inherited-members:

.. autoclass:: Indexes
    :members: default, delete
    :inherited-members:

.. autoclass:: Input
    :members: update
    :inherited-members:

.. autoclass:: Inputs
    :members: create, delete, itemmeta, kinds, kindpath, list, iter, oneshot
    :inherited-members:

.. autoclass:: InvalidNameException
    :members:

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

.. autoclass:: NoSuchCapability
    :members:

.. autoclass:: NotSupportedError
    :members:

.. autoclass:: OperationError
    :members:

.. autoclass:: ReadOnlyCollection
    :members: itemmeta, iter, list, names
    :inherited-members:

.. autoclass:: Role
    :members: grant, revoke
    :inherited-members:

.. autoclass:: Roles
    :members: create, delete
    :inherited-members:

.. autoclass:: SavedSearch
    :members: acknowledge, alert_count, dispatch, fired_alerts, history, scheduled_times, suppress, suppressed, unsuppress, update
    :inherited-members:

.. autoclass:: SavedSearches
    :members: create
    :inherited-members:

.. autoclass:: Service
    :members: apps, confs, capabilities, event_types, fired_alerts, indexes, info, inputs, job, jobs, loggers, messages, modular_input_kinds, parse, restart, restart_required, roles, search, saved_searches, settings, splunk_version, storage_passwords, users
    :inherited-members:

.. autoclass:: Settings
    :members: update
    :inherited-members:

.. autoclass:: Stanza
    :members: submit
    :inherited-members:

.. autoclass:: StoragePassword
    :members: clear_password, encrypted_password, realm, username
    :inherited-members:

.. autoclass:: StoragePasswords
    :members: create, delete
    :inherited-members:

.. autoclass:: User
    :members: role_entities
    :inherited-members:

.. autoclass:: Users
    :members: create, delete
    :inherited-members:
