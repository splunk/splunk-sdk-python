# Binding constants
# If you change these, update the docstring
# on _authority as well.
DEFAULT_HOST = "localhost"
DEFAULT_PORT = "8089"
DEFAULT_SCHEME = "https"

# Client Module Constants
PATH_APPS = "apps/local/"
PATH_CAPABILITIES = "authorization/capabilities/"
PATH_CONF = "configs/conf-%s/"
PATH_PROPERTIES = "properties/"
PATH_DEPLOYMENT_CLIENTS = "deployment/client/"
PATH_DEPLOYMENT_TENANTS = "deployment/tenants/"
PATH_DEPLOYMENT_SERVERS = "deployment/server/"
PATH_DEPLOYMENT_SERVERCLASSES = "deployment/serverclass/"
PATH_EVENT_TYPES = "saved/eventtypes/"
PATH_FIRED_ALERTS = "alerts/fired_alerts/"
PATH_INDEXES = "data/indexes/"
PATH_INPUTS = "data/inputs/"
PATH_JOBS = "search/jobs/"
PATH_JOBS_V2 = "search/v2/jobs/"
PATH_LOGGER = "/services/server/logger/"
PATH_MESSAGES = "messages/"
PATH_MODULAR_INPUTS = "data/modular-inputs"
PATH_ROLES = "authorization/roles/"
PATH_SAVED_SEARCHES = "saved/searches/"
PATH_STANZA = "configs/conf-%s/%s"  # (file, stanza)
PATH_USERS = "authentication/users/"
PATH_RECEIVERS_STREAM = "/services/receivers/stream"
PATH_RECEIVERS_SIMPLE = "/services/receivers/simple"
PATH_STORAGE_PASSWORDS = "storage/passwords"

XNAMEF_ATOM = "{http://www.w3.org/2005/Atom}%s"
XNAME_ENTRY = XNAMEF_ATOM % "entry"
XNAME_CONTENT = XNAMEF_ATOM % "content"

MATCH_ENTRY_CONTENT = f"{XNAME_ENTRY}/{XNAME_CONTENT}/*"

# Data Module constants
# LNAME refers to element names without namespaces; XNAME is the same
# name, but with an XML namespace.
LNAME_DICT = "dict"
LNAME_ITEM = "item"
LNAME_KEY = "key"
LNAME_LIST = "list"

XNAMEF_REST = "{http://dev.splunk.com/ns/rest}%s"
XNAME_DICT = XNAMEF_REST % LNAME_DICT
XNAME_ITEM = XNAMEF_REST % LNAME_ITEM
XNAME_KEY = XNAMEF_REST % LNAME_KEY
XNAME_LIST = XNAMEF_REST % LNAME_LIST
