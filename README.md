# xml_objects
Create Python objects from XML using decorated functions to parse the nodes.

## Usage
### Basic Parsers
This package relies on the creation of "parsers" to parse "nodes".

Consider this XML:

```
<root>
<title>Tis is a title</title>
<text>This is some text</text>
</root>
```

Three nodes are present: `root`, `title`, and `text`. All of these must be coded in Python:

```
from xml_objects import Builder, no_parent

builder = Builder()


@builder.parser('root')
def root_node(parent, text):
    """This is the root node, so parent should be no_parent."""
    assert parent is no_parent
    print('Parsing has begun.')


@builder.parser('title')
def show_title(parent, text):
    """Because nothing was returned by the root parser, parent should be None."""
    assert parent is None
    print('Title: %s' % text)
    return text


@builder.parser('text')
def show_text(parent, text):
    """Because we returned title from the title parser, we can show it now too."""
    print('%s -> %s' % (parent, text))
```

With setup now complete, we could use the `from_string` method of Builder to print the messages, like so:

```builder.from_string(xml)```

### Attributes
Attributes can be used to provide keyword arguments to your parsers. Consider this example node from the Flask example:

```
<app name="flask-app" host="0.0.0.0" port="8000">
...
</app>```

The app parser in `xml_objects/ext/flask.py` expects `name`, `host`, and `port` as keyword arguments, and provides sensible defaults accordingly:

```
@builder.parser('app')
def get_app(parent, text, name=__name__, host='0.0.0.0', port='4000'):
    """Returns a flask app."""
    if parent is not no_parent:
        raise RuntimeError(
            'This must be the top-level tag.\nparent: %r' % parent
        )
    app = Flask(name)
    app.config['HOST'] = host
    app.config['PORT'] = int(port)
    return app
```

### Storage
While you could use xml_objects to build GUIs with [wxPython](https://wxpython.org/) for example, xml_objects itself doesn't provide any mechanism to store state, so this must be done by the programmer.

For examples, see `xml_objects/ext/wx.py`.