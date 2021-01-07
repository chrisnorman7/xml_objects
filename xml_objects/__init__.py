"""The xml_objects library.

A library for converting XML into python objects.

Provides the Builder class.
"""

from typing import Any, IO, Callable, Dict, Generic, Optional, TypeVar
from xml.etree.ElementTree import Element, ElementTree, fromstring, parse

from attr import Factory, attrib, attrs

InputObjectType = TypeVar('InputObjectType')
OutputObjectType = TypeVar('OutputObjectType')
TextType = Optional[str]
AttribType = Dict[str, str]
MakerType = Callable[[Optional[InputObjectType], Element], OutputObjectType]
ParserType = Callable[[OutputObjectType, Element], OutputObjectType]
NoneType = type(None)


class XMLObjectsException(Exception):
    """Base exception."""


class UnhandledElement(XMLObjectsException):
    """No such parser has been defined."""


@attrs(auto_attribs=True)
class Builder(Generic[InputObjectType, OutputObjectType]):
    """A builder for returning python objects from xml ``Element`` instances.

    Given a single node and a input object, a builder can transform the input
    object according to the data found in the provided element.

    To parse a tag, use the :meth:`~Builder.parse_element` method.

    :ivar ~Builder.maker: The method which will make an initial object for this
        builder to work on.

    :ivar ~Builder.name: A name to differentiate a builder when debugging.

    :ivar ~Builder>parsers: A dictionary of parser functions mapped to tag
        names.

    :ivar ~Builder.builders: A dictionary a sub builders, mapped to tag names.
    """

    maker: MakerType

    name: Optional[str] = None
    parsers: Dict[str, ParserType] = attrib(default=Factory(dict), repr=False)
    builders: Dict[str, 'Builder'] = attrib(default=Factory(dict), repr=False)

    def make_object(self, element: Element) -> OutputObjectType:
        """Make an initial object for this builder to work on.

        This value will not be stored anywhere on this builder, so its
        lifecycle is completely up to the programmer.

        :param element: The element to build the object from.
        """
        return self.maker(None, element)

    def make_and_handle(self, element: Element) -> OutputObjectType:
        """Make the initial object, then handle the element.

        :param element: The element to handle."""
        obj:

    def handle_element(
        self, element: Element, input_object: InputObjectType
    ) -> OutputObjectType:
        """Handle the given element, as well as all child elements.

        :param element: The parent to work on.

        :param input_object: The object which has been created by any previous
            parsers.
        """
        output_object: OutputObjectType
        tag: str = element.tag
        if tag in self.parsers:
            output_object = self.parsers[tag](input_object, element)
        elif tag in self.builders:
            builder: Builder[OutputObjectType, Any] = self.builders[tag]
            obj: Any = builder.maker(element, )
            return builder.handle_element(
                element, input_object
            )
        else:
            raise UnhandledElement(self, element)
        child: Element
        for child in element:
            self.handle_element(child, output_object)
        return output_object

    def handle_string(self, xml: str) -> OutputObjectType:
        """Parse and handle an element from a string.

        :param xml: The xml string to parse.
        """
        element: Element = fromstring(xml)
        return self.handle_element(element, None)

    def handle_file(self, fileobj: IO[str]) -> OutputObjectType:
        """Handle a file-like object.

        :param fileobj: The file-like object to read XML from.
        """
        return self.handle_string(fileobj.read())

    def handle_filename(self, filename: str) -> OutputObjectType:
        """Return an element made from a file with the given name.

        :param filename: The name of the file to load.
        """
        root: ElementTree = parse((filename))
        e: Element = root.getroot()
        return self.handle_element(e, None)

    def parser(self, tag: str) -> Callable[[ParserType], ParserType]:
        """Add a new parser to this builder.

        Parsers work on the name on a tag. So if you wish to work on the XML
        ``<title>Hello, title</title>``, you need a parser that knows how to
        handle the ``title`` tag.

        :param tag: The tag name this parser will handle.
        """

        def inner(func: ParserType) -> ParserType:
            """Add ``func`` to the :attr:`~Builder.parsers` dictionary.

            :param func: The function to add.
            """
            self.add_parser(tag, func)
            return func

        return inner

    def add_parser(self, tag: str, func: ParserType) -> None:
        """Add a parser to this builder.

        :param tag: The name of the tag that this parser knows how to handle.

        :param func: The function which will do the actual parsing.
        """
        self.parsers[tag] = func

    def add_builder(self, tag: str, builder: 'Builder') -> None:
        """Add a sub builder to this builder.

        In the same way that parsers know how to handle a single tag, sub
        builders can handle many tags recursively.

        :param tag: The name of the top level tag this sub builder knows how to
            handle.

        :param builder: The builder to add.
        """
        self.builders[tag] = builder
