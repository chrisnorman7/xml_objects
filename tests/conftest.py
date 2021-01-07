"""Configure tests."""

from typing import Any, Optional
from xml.etree.ElementTree import Element, ElementTree, parse

from pytest import fixture

from xml_objects import Builder


@fixture(name='b')
def builder() -> Builder:
    """Return a Builder instance."""
    def maker(parent: Optional[Any], element: Element) -> str:
        return element.tag

    return Builder(maker)


@fixture(name='e')
def get_element() -> Element:
    """Return a tree loaded from the included world.xml file."""
    tree: ElementTree = parse('world.xml')
    return tree.getroot()
