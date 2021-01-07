"""Test the Builder class."""

from typing import Any, List, Optional, Union
from xml.etree.ElementTree import Element

from attr import Factory, attrs
from pytest import raises

from xml_objects import Builder, UnhandledElement


@attrs(auto_attribs=True)
class PretendWeapon:
    """A pretend weapon."""

    name: str = 'Unnamed Weapon'
    type: str = 'sword'


@attrs(auto_attribs=True)
class PretendPerson:
    """A pretend person."""

    name: str = 'Unnamed Person'
    weapon: Optional[PretendWeapon] = None


@attrs(auto_attribs=True)
class BaseObject:
    """A base test object."""

    title: str = 'Untitled Object'
    description: str = 'You see nothing special.'
    people: List[PretendPerson] = Factory(list)


def get_object(parent: Optional[BaseObject], element: Element) -> BaseObject:
    """Return a BaseObject instance."""
    return BaseObject()


def get_title(parent: Optional[BaseObject], element: Element) -> BaseObject:
    """Add a title."""
    assert parent is not None
    if element.text is not None:
        parent.title = element.text
    return parent


def get_description(
    parent: Optional[BaseObject], element: Element
) -> BaseObject:
    """Set the description."""
    assert parent is not None
    if element.text is not None:
        parent.description = element.text
    return parent


def test_init(b: Builder) -> None:
    """Test initialisation."""
    assert isinstance(b, Builder)
    assert b.parsers == {}


def test_unhandled_element(b: Builder) -> None:
    """Test that unhandled elements work properly."""
    e: Element = Element('test', hello='world')
    with raises(UnhandledElement) as exc:
        b.handle_element(e, None)
    assert exc.value.args == (b, e)


def test_handle_one_level() -> None:
    """Handle a single level of tags, with no sub builders."""
    b: Builder[BaseObject] = Builder()
    b.add_parser('object', get_object)
    b.add_parser('title', get_title)
    b.add_parser('description', get_description)
    root: Element = Element('object')
    title: Element = Element('title')
    title.text = 'Test Title'
    description: Element = Element('description')
    description.text = 'A very nice description.'
    root.extend([title, description])
    o: BaseObject = b.handle_element(root, None)
    assert isinstance(o, BaseObject)
    assert o.title == title.text
    assert o.description == description.text
    assert o.people == []


def test_handle_multiple_levels() -> None:
    """Handle multiple levels of children."""
    weapon_builder: Builder[PretendPerson] = Builder(name='Weapon builder')

    @weapon_builder.parser('weapon')
    def get_weapon(
        person: Optional[PretendPerson], element: Element
    ) -> PretendPerson:
        """Get a pretend weapon."""
        assert person is not None
        w: PretendWeapon = PretendWeapon()
        person.weapon = w
        return person

    @weapon_builder.parser('type')
    def get_type(
        parent: Optional[PretendWeapon], element: Element
    ) -> PretendWeapon:
        """Get a weapon type."""
        assert parent is not None
        if element.text is not None:
            parent.type = element.text
        return parent

    person_builder: Builder[PretendPerson] = Builder(
        name='Person builder', builders={'weapon': weapon_builder}
    )

    @person_builder.parser('person')
    def get_person(
        parent: Optional[PretendPerson], element: Element
    ) -> PretendPerson:
        """Get a pretend person."""
        return PretendPerson()

    def get_name(
        parent: Optional[Union[PretendPerson, PretendWeapon]], element: Element
    ) -> Any:
        """Get a name."""
        if parent is not None and element.text is not None:
            parent.name = element.text
        return parent

    person_builder.add_parser('name', get_name)
    weapon_builder.add_parser('name', get_name)
    object_builder: Builder[BaseObject] = Builder(
        name='Object builder', parsers={
            'object': get_object,
            'title': get_title,
            'description': get_description
        }, builders={
            'person': person_builder,
        }
    )
    xml: str = '''<object>
        <title>New World</title>
        <description>Something exciting.</description>
        <person>
            <name>John</name>
            <weapon>
                <name>Codebreaker</name>
            </weapon>
        </person>
        <person>
            <name>Ellie</name>
            <weapon>
                <name>Code Fixer</name>
                <type>hammer</type>
            </weapon>
        </person>
    </object>'''
    o: BaseObject = object_builder.handle_string(xml)
    assert isinstance(o, BaseObject)
    assert o.title == 'New World'
    assert o.description == 'Something exciting.'
    assert len(o.people) == 2
