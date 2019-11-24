"""Provides the FlaskBuilder class."""

from functools import partial

from flask import Flask, render_template_string

from .. import Builder, no_parent

builder = Builder()


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


@builder.parser('route')
def get_route(app, text, path=None):
    """Decorates a function as a route."""
    if not isinstance(app, Flask):
        raise RuntimeError(
            'This tag must be used inside an app block. Parent was %r.' % app
        )
    if path is None:
        raise RuntimeError('A path must be supplied.')
    f = partial(render_template_string, text)
    f.__name__ = path.replace('/', '_')
    return app.route(path)(f)
