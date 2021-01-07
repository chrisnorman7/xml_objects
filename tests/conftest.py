"""Configure tests."""

from xml.etree.ElementTree import Element, fromstring

from pytest import fixture

from xml_objects import Builder


@fixture(name='b')
def builder() -> Builder:
    """Return a Builder instance."""
    return Builder()


@fixture(name='e')
def get_element() -> Element:
    """Return a tree loaded from the included world.xml file."""
    with open('world.xml', 'r') as f:
        return fromstring(f.read())
