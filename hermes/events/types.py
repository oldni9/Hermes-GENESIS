"""
===============================================================================
Hermes Event Types
===============================================================================
"""


class Events:

    # Runtime

    RUNTIME_BOOT = "runtime.boot"

    RUNTIME_READY = "runtime.ready"

    RUNTIME_SHUTDOWN = "runtime.shutdown"

    # Providers

    PROVIDER_CHANGED = "provider.changed"

    MODEL_CHANGED = "provider.model.changed"

    # Files

    FILE_CREATED = "files.created"

    FILE_DELETED = "files.deleted"

    FILE_MOVED = "files.moved"

    FILE_COPIED = "files.copied"

    FILE_INDEXED = "files.indexed"

    # Commands

    COMMAND_EXECUTED = "command.executed"

    COMMAND_FAILED = "command.failed"

    # Subsystems

    SUBSYSTEM_STARTED = "subsystem.started"

    SUBSYSTEM_STOPPED = "subsystem.stopped"
