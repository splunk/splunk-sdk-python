# Copyright 2011-2012 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""This module provides an Atom Feed response loader.

A simple :func:`load` utility reads Atom Feed XML data (the format returned by
the Splunk REST API), and converts it to a native Python dictionary or list.
"""

from xml.etree.ElementTree import XML

__all__ = ["load"]

LNAME_DICT = "dict"
LNAME_ITEM = "item"
LNAME_KEY = "key"
LNAME_LIST = "list"

XNAMEF_REST = "{http://dev.splunk.com/ns/rest}%s"
XNAME_DICT = XNAMEF_REST % LNAME_DICT
XNAME_ITEM = XNAMEF_REST % LNAME_ITEM
XNAME_KEY = XNAMEF_REST % LNAME_KEY
XNAME_LIST = XNAMEF_REST % LNAME_LIST

# Some responses don't use namespaces (eg: search/parse) so we look for
# both the extended and local versions of the following names.

def isdict(name):
    return name == XNAME_DICT or name == LNAME_DICT

def isitem(name):
    return name == XNAME_ITEM or name == LNAME_ITEM

def iskey(name):
    return name == XNAME_KEY or name == LNAME_KEY

def islist(name):
    return name == XNAME_LIST or name == LNAME_LIST

def hasattrs(element):
    return len(element.attrib) > 0

def localname(xname):
    rcurly = xname.find('}')
    return xname if rcurly == -1 else xname[rcurly+1:]

def load(text, match=None):
    """Loads XML text into a native Python structure (*dict* or *list*). If you
    provide an optional **match** string (a tag name or path), only the matching
    sub-elements are loaded. 

    :param `text`: The XML text to load.
    :type `text`: string
    :param `match`: A tag name or path to match (optional).
    :type `match`: string
    """
    if text is None: return None
    text = text.strip()
    if len(text) == 0: return None
    nametable = {
        'namespaces': [],
        'names': {}
    }
    root = XML(text)
    items = [root] if match is None else root.findall(match)
    count = len(items)
    if count == 0: return None
    if count == 1: return load_root(items[0], nametable)
    return [ load_root(item, nametable) for item in items ]

# Load the attributes of the given element.
def load_attrs(element):
    if not hasattrs(element): return None
    attrs = record()
    for key, value in element.attrib.iteritems(): 
        attrs[key] = value
    return attrs

# Parse a <dict> element and return a Python dict
def load_dict(element, nametable = None):
    value = record()
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
    if attrs is None: return name, value
    if value is None: return name, attrs
    # If value is simple, merge into attrs dict using special key
    if isinstance(value, str):
        attrs["$text"] = value
        return name, attrs
    # Both attrs & value are complex, so merge the two dicts
    for key, val in attrs.iteritems():
        #assert not value.has_key(k) # Assume no collisions
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
    if isdict(tag): return load_dict(element, nametable)
    if islist(tag): return load_list(element, nametable)
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
        text = text.strip()
        if len(text) == 0: 
            return None
        return text

    # Look for the special case of a single well-known structure
    if count == 1:
        child = children[0]
        tag = child.tag
        if isdict(tag): return load_dict(child, nametable)
        if islist(tag): return load_list(child, nametable)

    value = record()
    for child in children:
        name, item = load_elem(child, nametable)
        # If we have seen this name before, promote the value to a list
        if value.has_key(name):
            current = value[name]
            if not isinstance(current, list): 
                value[name] = [current]
            value[name].append(item)
        else:
            value[name] = item

    return value

# A generic utility that enables "dot" access to dicts
class Record(dict):
    """A generic utility class that enables dot access to members of 
    a Python dictionary.

    Any key which is also a valid Python identifier can be fetched as
    a field, so for a Record ``r``, ``r.key`` is equivalent to
    ``r['key']``. A key like ``invalid-key`` or ``invalid.key`` cannot
    be fetched as a field, since ``-`` and ``.`` are not allowed in
    identifiers.

    However, keys of the form ``a.b.c`` are very natural to write in
    Python as fields, so Record does something sane with them: if a
    group of keys all share a prefix ending in ``.``, then you can
    fetch them as a nested dictionary by calling just the prefix,
    e.g., if Record ``r`` contains keys ``'foo'``, ``'bar.baz'``, and
    ``'bar.qux'``, ``r.bar`` returns a Record with the keys ``baz``
    and ``qux``. If there are multiple ``.``'s in the key, each ``.``
    is put into a nested dictionary. Thus you can write ``r.bar.qux``
    or ``r['bar.qux']`` interchangeably.
    """
    sep = '.'

    def __call__(self, *args):
        if len(args) == 0: return self
        return Record((key, self[key]) for key in args)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError: 
            raise AttributeError(name)

    def __delattr__(self, name):
        del self[name]

    def __setattr__(self, name, value):
        self[name] = value

    @staticmethod
    def fromkv(k, v):
        result = record()
        result[k] = v
        return result

    def __getitem__(self, key):
        if key in self:
            return dict.__getitem__(self, key)
        key = key + self.sep
        result = record()
        for k,v in self.iteritems():
            if not k.startswith(key):
                continue
            suffix = k[len(key):]
            if '.' in suffix:
                ks = suffix.split(self.sep)
                z = result
                for x in ks[:-1]:
                    if x not in z:
                        z[x] = record()
                    z = z[x]
                z[ks[-1]] = v
            else:
                result[suffix] = v
        if len(result) == 0:
            raise KeyError("No key or prefix: %s" % key)
        return result
    

def record(value=None): 
    """Returns a **record** instance constructed with an initial value that you
    provide.
    
    :param `value`: An initial record value.
    :type `value`: dict
    """
    if value is None: value = {}
    return Record(value)

