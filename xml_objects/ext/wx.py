import wx

from xml_objects import Builder, no_parent

builder = Builder()


def get_panel_sizer(parent):
    """Returns a tuple containing (panel, sizer), or raises AssertionError."""
    if isinstance(parent, wx.Frame):
        return (parent.panel, None)
    elif isinstance(parent, wx.BoxSizer):
        return (parent.frame.panel, parent)
    else:
        raise AssertionError(
            'Parent is neither a frame or a box sizer: %r.' % parent
        )


@builder.parser('frame')
def get_frame(parent, text, title='Untitled Frame'):
    """Return a wx.Frame instance."""
    assert parent is no_parent
    f = wx.Frame(None, name='', title=title)
    f.panel = wx.Panel(f)
    return f


@builder.parser('sizer')
def get_sizer(parent, text, orient='vertical'):
    """Get a sizer to add controls to."""
    orient = orient.upper()
    o = getattr(wx, orient)
    s = wx.BoxSizer(o)
    if isinstance(parent, wx.Frame):
        s.frame = parent
    elif isinstance(parent, wx.BoxSizer):
        s.frame = parent.frame
    else:
        raise AssertionError(
            'Parent must be a frame or a sizer. Got: %r' % parent
        )
    return s


@builder.parser('input')
def get_control(parent, text, type=None, style=None, label=None):
    """Get a button."""
    p, s = get_panel_sizer(parent)
    types = {
        None: wx.TextCtrl,
        'text': wx.TextCtrl,
        'checkbox': wx.CheckBox,
        'button': wx.Button
    }
    if type not in types:
        valid_types = ', '.join(types.keys())
        raise RuntimeError(
            'Invalid type: %r.\nValid types: %s' % (type, valid_types)
        )
    cls = types[type]
    kwargs = {'name': ''}
    if label is not None:
        kwargs['label'] = label
    if style is not None:
        style_int = 0
        for style_name in style.split(' '):
            style_value = getattr(wx, style_name.upper())
            style_int |= style_value
        kwargs['style'] = style_int
    print(kwargs)
    c = cls(p, **kwargs)
    if text is not None:
        text = text.strip()
        c.SetValue(text)
    s.Add(c, 1, wx.GROW)
    return c


@builder.parser('label')
def get_label(parent, text):
    """Create a label."""
    p, s = get_panel_sizer(parent)
    label = wx.StaticText(p, label=text.strip())
    s.Add(label, 0, wx.GROW)
    return label
