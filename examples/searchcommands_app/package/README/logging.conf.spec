#
# The format of this file is described in this article at Python.org:
#
#     [Configuration file format](http://goo.gl/K6edZ8)
#
# This file must contain sections called [loggers], [handlers] and [formatters] which identify by name the entities of
# each type which are defined in the file. For each such entity, there is a separate section which identifies how that
# entity is configured. Thus, for a logger named log01 in the [loggers] section, the relevant configuration details are
# held in a section [logger_log01]. Similarly, a handler called hand01 in the [handlers] section will have its
# configuration held in a section called [handler_hand01], while a formatter called form01 in the [formatters] section
# will have its configuration specified in a section called [formatter_form01]. The root logger configuration must be
# specified in a section called [logger_root].

[loggers]
    * Specifies a list of logger keys.

keys = <comma-separated strings>
    * A comma-separated list of logger keys. Each key must have a corresponding [logger_<string>] section in the
    * configuration file.
    * Defaults to empty.

[logger_root]
    * Specifies the configuration of the root logger.
    * The root logger must specify a level and a list of handlers.

level = [critical|error|warning|info|debug|notset]
    * Can be one of debug, info, warning, error, critical or notset. For the root logger only, notset means that all
    * messages will be logged. Level values are evaluated in the context of the logging package’s namespace.
    * Defaults to warning.

handlers = <comma-separated strings>
    * A comma-separated list of handler names, which must appear in the [handlers] section. These names must appear in
    * the [handlers] section and have corresponding sections in the configuration file.
    * Defaults to stderr.

[logger_<string>]
    * Specifies the configuration of a logger.

qualname = <string>
    * The hierarchical channel name of the logger, that is to say the name used by the application to get the logger.
    * A value is required.

level = [critical|error|warning|info|debug|notset]
    * Can be one of debug, info, warning, error, critical or notset. For the root logger only, notset means that all
    * messages will be logged. Level values are evaluated in the context of the logging package’s namespace.
    * Defaults to warning

handlers = <comma-separated strings>
    * A comma-separated list of handler names, which must appear in the [handlers] section. These names must appear in
    * the [handlers] section and have corresponding sections in the configuration file.
    * Defaults to stderr.

propagate = [0|1]
    * Set to 1 to indicate that messages must propagate to handlers higher up the logger hierarchy from this logger, or
    * 0 to indicate that messages are not propagated to handlers up the hierarchy.
    * Defaults to 1.

[handlers]
    * Specifies a list of handler keys.
    * See [logging.handlers](http://goo.gl/9aoOx)

keys = <comma-separated strings>
    * A comma-separated list of handlers keys. Each key must have a corresponding [handler_<string>] section in the
    * configuration file.
    * Defaults to empty.

[handler_<string>]
    * Specifies the configuration of a handler.

args = <string>
    * When evaluated in the context of the logging package’s namespace, is the list of arguments to the constructor for
    * the handler class.

class = <string>
    * Specifies the handler’s class as determined by eval() in the logging package’s namespace.
    * Defaults to logging.FileHandler.

level = [critical|error|warning|info|debug|notset]
    * Can be one of debug, info, warning, error, critical or notset. This value is interpreted as for loggers, and
    * notset is taken to mean, "log everything."

formatter = <string>
    * Specifies the key name of the formatter for this handler. If a name is specified, it must appear in the
    * [formatters] section and have a corresponding section in the configuration file.
    * Defaults to logging._defaultFormatter.

[formatters]
    * Specifies a list of formatter keys.
    * See [logging.formatters](http://goo.gl/z5CBR3)

keys = <comma-separated strings>
    * A comma-separated list of formatter keys. Each key must have a corresponding [formatter_<string>] section in the
    * configuration file.
    * Defaults to empty.

[formatter_<string>]
    * Specifies the configuration of a formatter.

class = <string>
    * The name of the formatter’s class as a dotted module and class name. This setting is useful for instantiating a
    * Formatter subclass. Subclasses of Formatter can present exception tracebacks in an expanded or condensed format.
    * Defaults to logging.Formatter.

datefmt = <string>
    * The strftime-compatible date/time format string. If empty, the package substitutes ISO8601 format date/times.
    * An example ISO8601 date/time is datetime(2015, 2, 6, 15, 53, 36, 786309).isoformat() ==
    * '2015-02-06T15:53:36.786309'. For a complete list of formatting directives, see section [strftime() and strptime()
    * Behavior](http://goo.gl/6zUAGv)
    * Defaults to empty.

format = <string>
    * The overall format string. This string uses %(<dictionary key>)s styled string substitution; the possible keys are
    * documented in [LogRecord](http://goo.gl/qW83Dg) attributes. The following format string will log the time in a
    * human-readable format, the severity of the message, and the contents of the message, in that order:
    *    format = '%(asctime)s - %(levelname)s - %(message)s'
    * A value is required.
