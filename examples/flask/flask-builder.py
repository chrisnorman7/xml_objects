from xml_python.ext.flask import FlaskBuilder

if __name__ == '__main__':
    builder = FlaskBuilder()
    app = builder.from_args('app.xml')
    app.run(host=app.config['HOST'], port=app.config['PORT'])
