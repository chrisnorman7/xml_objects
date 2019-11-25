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
