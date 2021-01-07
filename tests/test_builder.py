"""Test the Builder class."""

from typing import List, Optional, Union
from xml.etree.ElementTree import Element

from attr import Factory, attrs
from pytest import raises

from xml_python import Builder, NoneType, UnhandledElement


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


def get_object(parent: NoneType, element: Element) -> BaseObject:
    """Return a BaseObject instance."""
    return BaseObject()


def get_title(parent: BaseObject, element: Element) -> None:
    """Add a title."""
    if element.text is not None:
        parent.title = element.text


def get_description(parent: BaseObject, element: Element) -> None:
    """Set the description."""
    if element.text is not None:
        parent.description = element.text


def test_init(b: Builder) -> None:
    """Test initialisation."""
    assert isinstance(b, Builder)
    assert b.parsers == {}
    assert b.builders == {}


def test_unhandled_element(b: Builder) -> None:
    """Test that unhandled elements work properly."""
    root: Element = Element('whatever')
    e: Element = Element('test', hello='world')
    root.append(e)
    with raises(UnhandledElement) as exc:
        b.build(None, root)
    assert exc.value.args == (b, e)


def test_handle_one_level() -> None:
    """Handle a single level of tags, with no sub builders."""
    b: Builder[NoneType, BaseObject] = Builder(get_object)
    b.add_parser('title', get_title)
    b.add_parser('description', get_description)
    root: Element = Element('object')
    title: Element = Element('title')
    title.text = 'Test Title'
    description: Element = Element('description')
    description.text = 'A very nice description.'
    root.extend([title, description])
    o: BaseObject = b.build(None, root)
    assert isinstance(o, BaseObject)
    assert o.title == title.text
    assert o.description == description.text
    assert o.people == []


def test_handle_multiple_levels() -> None:
    """Handle multiple levels of children."""

    def get_weapon(
        person: Optional[PretendPerson], element: Element
    ) -> PretendWeapon:
        """Get a pretend weapon."""
        w: PretendWeapon = PretendWeapon()
        if person is not None:
            person.weapon = w
        return w

    weapon_builder: Builder[PretendPerson, PretendWeapon] = Builder(
        get_weapon, name='Weapon builder'
    )

    @weapon_builder.parser('type')
    def get_type(parent: PretendWeapon, element: Element) -> None:
        """Get a weapon type."""
        if element.text is not None:
            parent.type = element.text

    def get_person(
        parent: Optional[BaseObject], element: Element
    ) -> PretendPerson:
        """Get a pretend person."""
        person: PretendPerson = PretendPerson()
        if parent is not None:
            parent.people.append(person)
        return person

    person_builder: Builder[BaseObject, PretendPerson] = Builder(
        get_person, name='Person builder', builders={'weapon': weapon_builder}
    )

    def get_name(
        parent: Union[PretendPerson, PretendWeapon], element: Element
    ) -> None:
        """Get a name."""
        if element.text is not None:
            parent.name = element.text

    person_builder.add_parser('name', get_name)
    weapon_builder.add_parser('name', get_name)
    object_builder: Builder[NoneType, BaseObject] = Builder(
        get_object, name='Object builder', parsers={
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
            <name>Bill</name>
            <weapon>
                <name>Codebreaker</name>
            </weapon>
        </person>
        <person>
            <name>Jane</name>
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
    bill, jane = o.people
    assert isinstance(bill, PretendPerson)
    assert bill.name == 'Bill'
    w = bill.weapon
    assert isinstance(w, PretendWeapon)
    assert w.name == 'Codebreaker'
    assert w.type == 'sword'
    assert isinstance(jane, PretendPerson)
    assert jane.name == 'Jane'
    w = jane.weapon
    assert isinstance(w, PretendWeapon)
    assert w.name == 'Code Fixer'
    assert w.type == 'hammer'
