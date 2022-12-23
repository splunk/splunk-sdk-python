# Some responses don't use namespaces (eg: search/parse) so we look for
# both the extended and local versions of the following names.
from xml.etree.ElementTree import XML

from splunklib.constants import XNAME_DICT, LNAME_DICT, XNAME_ITEM, LNAME_ITEM, LNAME_KEY, XNAME_KEY, XNAME_LIST, \
    LNAME_LIST
from .Record import Record


def isdict(name):
    return name in (XNAME_DICT, LNAME_DICT)


def isitem(name):
    return name in (XNAME_ITEM, LNAME_ITEM)


def iskey(name):
    return name in (XNAME_KEY, LNAME_KEY)


def islist(name):
    return name in (XNAME_LIST, LNAME_LIST)


def hasattrs(element):
    return len(element.attrib) > 0


def localname(xname):
    rcurly = xname.find('}')
    return xname if rcurly == -1 else xname[rcurly + 1:]


def load(text, match=None):
    """This function reads a string that contains the XML of an Atom Feed, then
    returns the
    data in a native Python structure (a ``dict`` or ``list``). If you also
    provide a tag name or path to match, only the matching sub-elements are
    loaded.

    :param text: The XML text to load.
    :type text: ``string``
    :param match: A tag name or path to match (optional).
    :type match: ``string``
    """
    if text is None:
        return None
    text = text.strip()
    if len(text) == 0:
        return None
    nametable = {
        'namespaces': [],
        'names': {}
    }

    root = XML(text)
    items = [root] if match is None else root.findall(match)
    count = len(items)
    if count == 0:
        return None
    if count == 1:
        return load_root(items[0], nametable)
    return [load_root(item, nametable) for item in items]


# Load the attributes of the given element.
def load_attrs(element):
    if not hasattrs(element):
        return None
    attrs = Record()
    for key, value in list(element.attrib.items()):
        attrs[key] = value
    return attrs


# Parse a <dict> element and return a Python dict
def load_dict(element, nametable=None):
    value = Record()
    children = list(element)
    for child in children:
        assert iskey(child.tag)
        name = child.attrib["name"]
        value[name] = load_value(child, nametable)
    return value


# Loads the given elements attrs & value into single merged dict.
def load_elem(element, nametable=None):
    name = localname(element.tag)
    attrs = load_attrs(element)
    value = load_value(element, nametable)
    if attrs is None:
        return name, value
    if value is None:
        return name, attrs
    # If value is simple, merge into attrs dict using special key
    if isinstance(value, str):
        attrs["$text"] = value
        return name, attrs
    # Both attrs & value are complex, so merge the two dicts, resolving collisions.
    collision_keys = []
    for key, val in list(attrs.items()):
        if key in value and key in collision_keys:
            value[key].append(val)
        elif key in value and key not in collision_keys:
            value[key] = [value[key], val]
            collision_keys.append(key)
        else:
            value[key] = val
    return name, value


# Parse a <list> element and return a Python list
def load_list(element, nametable=None):
    assert islist(element.tag)
    value = []
    children = list(element)
    for child in children:
        assert isitem(child.tag)
        value.append(load_value(child, nametable))
    return value


# Load the given root element.
def load_root(element, nametable=None):
    tag = element.tag
    if isdict(tag):
        return load_dict(element, nametable)
    if islist(tag):
        return load_list(element, nametable)
    k, v = load_elem(element, nametable)
    return Record.fromkv(k, v)


# Load the children of the given element.
def load_value(element, nametable=None):
    children = list(element)
    count = len(children)

    # No children, assume a simple text value
    if count == 0:
        text = element.text
        if text is None:
            return None

        if len(text.strip()) == 0:
            return None
        return text

    # Look for the special case of a single well-known structure
    if count == 1:
        child = children[0]
        tag = child.tag
        if isdict(tag):
            return load_dict(child, nametable)
        if islist(tag):
            return load_list(child, nametable)

    value = Record()
    for child in children:
        name, item = load_elem(child, nametable)
        # If we have seen this name before, promote the value to a list
        if name in value:
            current = value[name]
            if not isinstance(current, list):
                value[name] = [current]
            value[name].append(item)
        else:
            value[name] = item

    return value
