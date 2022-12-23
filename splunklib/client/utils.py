import json

from splunklib.data import Record
from splunklib.data.utils import load


def _trailing(template, *targets):
    """Substring of *template* following all *targets*.

    **Example**::

        template = "this is a test of the bunnies."
        _trailing(template, "is", "est", "the") == " bunnies"

    Each target is matched successively in the string, and the string
    remaining after the last target is returned. If one of the targets
    fails to match, a ValueError is raised.

    :param template: Template to extract a trailing string from.
    :type template: ``string``
    :param targets: Strings to successively match in *template*.
    :type targets: list of ``string``s
    :return: Trailing string after all targets are matched.
    :rtype: ``string``
    :raises ValueError: Raised when one of the targets does not match.
    """
    s = template
    for t in targets:
        n = s.find(t)
        if n == -1:
            raise ValueError("Target " + t + " not found in template.")
        s = s[n + len(t):]
    return s


# Filter the given state content record according to the given arg list.
def _filter_content(content, *args):
    if len(args) > 0:
        return Record((k, content[k]) for k in args)
    return Record((k, v) for k, v in list(content.items())
                  if k not in ['eai:acl', 'eai:attributes', 'type'])


# Construct a resource path from the given base path + resource name
def _path(base, name):
    if not base.endswith('/'): base = base + '/'
    return base + name


# Load an atom record from the body of the given response
# this will ultimately be sent to an xml ElementTree so we
# should use the xmlcharrefreplace option
def _load_atom(response, match=None):
    return load(response.body.read()
                .decode('utf-8', 'xmlcharrefreplace'), match)


# Load an array of atom entries from the body of the given response
def _load_atom_entries(response):
    r = _load_atom(response)
    if 'feed' in r:
        # Need this to handle a random case in the REST API
        if r.feed.get('totalResults') in [0, '0']:
            return []
        entries = r.feed.get('entry', None)
        if entries is None: return None
        return entries if isinstance(entries, list) else [entries]
    # Unlike most other endpoints, the jobs endpoint does not return
    # its state wrapped in another element, but at the top level.
    # For example, in XML, it returns <entry>...</entry> instead of
    # <feed><entry>...</entry></feed>.
    entries = r.get('entry', None)
    if entries is None:
        return None
    return entries if isinstance(entries, list) else [entries]


# Load the sid from the body of the given response
def _load_sid(response, output_mode):
    if output_mode == "json":
        json_obj = json.loads(response.body.read())
        return json_obj.get('sid')
    return _load_atom(response).response.sid


# Parse the given atom entry record into a generic entity state record
def _parse_atom_entry(entry):
    title = entry.get('title', None)

    elink = entry.get('link', [])
    elink = elink if isinstance(elink, list) else [elink]
    links = Record((link.rel, link.href) for link in elink)

    # Retrieve entity content values
    content = entry.get('content', {})

    # Host entry metadata
    metadata = _parse_atom_metadata(content)

    # Filter some of the noise out of the content record
    content = Record((k, v) for k, v in list(content.items())
                     if k not in ['eai:acl', 'eai:attributes'])

    if 'type' in content:
        if isinstance(content['type'], list):
            content['type'] = [t for t in content['type'] if t != 'text/xml']
            # Unset type if it was only 'text/xml'
            if len(content['type']) == 0:
                content.pop('type', None)
            # Flatten 1 element list
            if len(content['type']) == 1:
                content['type'] = content['type'][0]
        else:
            content.pop('type', None)

    return Record({
        'title': title,
        'links': links,
        'access': metadata.access,
        'fields': metadata.fields,
        'content': content,
        'updated': entry.get("updated")
    })


# Parse the metadata fields out of the given atom entry content record
def _parse_atom_metadata(content):
    # Hoist access metadata
    access = content.get('eai:acl', None)

    # Hoist content metadata (and cleanup some naming)
    attributes = content.get('eai:attributes', {})
    fields = Record({
        'required': attributes.get('requiredFields', []),
        'optional': attributes.get('optionalFields', []),
        'wildcard': attributes.get('wildcardFields', [])})

    return Record({'access': access, 'fields': fields})

