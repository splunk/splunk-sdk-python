# A generic utility that enables "dot" access to dicts


class Record(dict):
    """This generic utility class enables dot access to members of a Python
    dictionary.

    Any key that is also a valid Python identifier can be retrieved as a field.
    So, for an instance of ``Record`` called ``r``, ``r.key`` is equivalent to
    ``r['key']``. A key such as ``invalid-key`` or ``invalid.key`` cannot be
    retrieved as a field, because ``-`` and ``.`` are not allowed in
    identifiers.

    Keys of the form ``a.b.c`` are very natural to write in Python as fields. If
    a group of keys shares a prefix ending in ``.``, you can retrieve keys as a
    nested dictionary by calling only the prefix. For example, if ``r`` contains
    keys ``'foo'``, ``'bar.baz'``, and ``'bar.qux'``, ``r.bar`` returns a record
    with the keys ``baz`` and ``qux``. If a key contains multiple ``.``, each
    one is placed into a nested dictionary, so you can write ``r.bar.qux`` or
    ``r['bar.qux']`` interchangeably.
    """
    sep = '.'

    def __call__(self, *args):
        if len(args) == 0:
            return self
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
        result = Record()
        result[k] = v
        return result

    def __getitem__(self, key):
        if key in self:
            return dict.__getitem__(self, key)
        key += self.sep
        result = Record()
        for k, v in list(self.items()):
            if not k.startswith(key):
                continue
            suffix = k[len(key):]
            if '.' in suffix:
                ks = suffix.split(self.sep)
                z = result
                for x in ks[:-1]:
                    if x not in z:
                        z[x] = Record()
                    z = z[x]
                z[ks[-1]] = v
            else:
                result[suffix] = v
        if len(result) == 0:
            raise KeyError(f"No key or prefix: {key}")
        return result
