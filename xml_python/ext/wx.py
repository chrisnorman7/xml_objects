import wx
from text2code import text2code as t2c

from .. import Builder, no_parent, parser


class WXBuilder(Builder):
    """Add a types attribute."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.types = {
            None: wx.TextCtrl,
            'text': wx.TextCtrl,
            'checkbox': wx.CheckBox,
            'button': wx.Button
        }
        self.event_globals = {
            'builder': self
        }

    @parser('frame')
    def get_frame(self, parent, text, title='Untitled Frame'):
        """Return a wx.Frame instance."""
        assert parent is no_parent
        f = wx.Frame(None, name='', title=title)
        f.panel = wx.Panel(f)
        return f

    @parser('sizer')
    def get_sizer(
        self, parent, text, name=None, proportion='1', orient='vertical'
    ):
        """Get a sizer to add controls to."""
        orient = orient.upper()
        o = getattr(wx, orient)
        if isinstance(parent, wx.Frame):
            f = parent
        elif isinstance(parent, wx.BoxSizer):
            f = parent.frame
        else:
            raise AssertionError(
                'Parent must be a frame or a sizer. Got: %r' % parent
            )
        s = wx.BoxSizer(o)
        s.frame = f
        if name is not None:
            setattr(f, name, s)
        yield s
        if isinstance(parent, wx.Frame):
            parent.panel.SetSizerAndFit(s)
        else:
            parent.Add(s, int(proportion), wx.GROW)

    @parser('input')
    def get_control(
        self, parent, text, proportion=1, name=None, type=None, style=None,
        label=None
    ):
        """Get a button."""
        p, s = self.get_panel_sizer(parent)
        if type not in self.types:
            valid_types = ', '.join(self.types.keys())
            raise RuntimeError(
                'Invalid type: %r.\nValid types: %s' % (type, valid_types)
            )
        cls = self.types[type]
        kwargs = {'name': ''}
        if label is not None:
            kwargs['label'] = label
        if style is not None:
            style_int = 0
            for style_name in style.split(' '):
                style_value = getattr(wx, style_name.upper())
                style_int |= style_value
            kwargs['style'] = style_int
        c = cls(p, **kwargs)
        if name is not None:
            setattr(p.GetParent(), name, c)
        if text is not None:
            text = text.strip()
            if text:
                c.SetValue(text)
        s.Add(c, int(proportion), wx.GROW)
        return c

    @parser('label')
    def get_label(
        self, parent, text, name=None, proportion='0'
    ):
        """Create a label."""
        p, s = self.get_panel_sizer(parent)
        label = wx.StaticText(p, label=text.strip())
        s.Add(label, int(proportion), wx.GROW)
        if name is not None:
            setattr(p.GetParent(), name, label)
        return label

    @parser('event')
    def get_event(self, parent, text, type=None):
        """Create an event using text2code."""
        if type is None:
            raise RuntimeError('You must provide a type.')
        event_name = 'evt_' + type
        event_name = event_name.upper()
        event_type = getattr(wx, event_name)
        stuff = t2c(text, __name__, **self.event_globals)
        if 'event' not in stuff:
            raise RuntimeError(
                'No function named "event" found in %r.' % stuff
            )
        f = stuff['event']
        parent.Bind(event_type, f)
        return parent  # Don't want anything untoward happening.

    @parser('menubar')
    def get_menubar(self, parent, text):
        """Create a menubar."""
        if not isinstance(parent, wx.Frame):
            raise RuntimeError(
                'This tag must be a child node of the frame tag.'
            )
        elif parent.GetMenuBar() is not None:
            raise RuntimeError('That frame already has a menubar.')
        mb = wx.MenuBar()
        parent.SetMenuBar(mb)
        return mb

    @parser('menu')
    def get_menu(self, parent, text, title=None, name=None):
        """Add a menu to the main menubar, or a submenu to an existing menu."""
        if isinstance(parent, wx.MenuBar):
            f = parent.GetTopLevelParent()
        elif isinstance(parent, wx.Menu):
            f = parent.GetWindow()
        else:
            raise RuntimeError('This tag must be a child of menubar, or menu.')
        if title is None:
            raise RuntimeError('Menus must have a title.')
        m = wx.Menu(title)
        if name is not None:
            setattr(f, name, m)
        yield m
        if isinstance(parent, wx.MenuBar):
            parent.Append(m, title)
        else:
            parent.AppendSubMenu(m, title)

    @parser('menuitem')
    def get_menuitem(
        self, parent, text, name=None, id='any', hotkey=None, help=''
    ):
        """Adds a menu item to a menu. Must be a child tag of menu."""
        if not isinstance(parent, wx.Menu):
            raise RuntimeError('Must be a child tag of menu.')
        if text is None:
            raise RuntimeError(
                'This tag must contain text to be used  as the title for the '
                'menu item.'
            )
        text = text.strip()
        if hotkey is not None:
            text += f'\t{hotkey}'
        id = f'ID_{id.upper()}'
        id = getattr(wx, id)
        i = parent.Append(id, text, help)
        return i

    def get_panel_sizer(self, parent):
        """Returns a tuple containing (panel, sizer), or raises
        AssertionError."""
        if isinstance(parent, wx.Frame):
            return (parent.panel, None)
        elif isinstance(parent, wx.BoxSizer):
            return (parent.frame.panel, parent)
        else:
            raise AssertionError(
                'Parent is neither a frame or a box sizer: %r.' % parent
            )
