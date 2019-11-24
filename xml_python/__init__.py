"""Provides the WorldBuilder class."""

import sys

from inspect import isgenerator
from xml.etree.ElementTree import fromstring


class NoParent:
    def __str__(self):
        return 'Top-level node'

    def __repr__(self):
        return str(self)


no_parent = NoParent()


class NoSuchParser(Exception):
    """No such parser has been defined."""


class Builder:
    """Subclass to create your own builder, or juse instantiate and use the
    parser decorator."""

    def __init__(self):
        """Set some defaults."""
        self.parsers = {}

    def parser(self, name):
        """Decorate a function to use as a parser.

        The function must be prepared to take at least two arguments:

        A "parent" object, which is the returned value from the parent parser,
        or no_parent if this is the first parser to be called.

        Any non-XML text from the current node.

        Any attributes of the node will be used as keyword arguments."""
        def inner(func):
            self.parsers[name] = func
            return func
        return inner

    def from_args(self, default):
        """Passes either sys.argv[1], or default to self.from_filename."""
        try:
            default = sys.argv[1]
        except IndexError:
            pass  # default will simply stay the same.
        return self.from_filename(default)

    def from_filename(self, filename):
        """Opens the given filename, and passes the file object onto
        self.from_file."""
        with open(filename, 'r') as f:
            return self.from_file(f)

    def from_file(self, f):
        """Passes f.read() onto self.from_string."""
        return self.from_string(f.read())

    def from_string(self, string):
        """Given an XML string, returns an object. All tags must have a
        corrisonding parser, decorated with self.parser."""
        root = fromstring(string)
        return self.build(root, no_parent)

    def build(self, node, parent):
        """Given an XML node (such as those returned by
        xml.etree.ElementTree.fromstring), return an object."""
        name = node.tag
        text = node.text
        if name not in self.parsers:
            raise NoSuchParser(name)
        parser = self.parsers[name]
        kwargs = {
            name.replace('-', '_'): value for name, value in
            node.attrib.items()
        }
        ret = parser(parent, text, **kwargs)
        if isgenerator(ret):
            obj = next(ret)
        else:
            obj = ret
        for child in node:
            self.build(child, obj)
        if isgenerator(ret):
            try:
                next(ret)
                raise RuntimeError(
                    'Iterators can only yield once.\nOffending parser: %r' %
                    parser
                )
            except StopIteration:
                pass  # Good stuff.
        return obj
