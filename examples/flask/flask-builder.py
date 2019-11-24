import sys

from xml_objects.ext.flask import builder

if __name__ == '__main__':
    try:
        filename = sys.argv[1]
    except IndexError:
        filename = 'app.xml'
    print('Loading file %s...' % filename)
    app = builder.from_filename(filename)
    app.run(host=app.config['HOST'], port=app.config['PORT'])
