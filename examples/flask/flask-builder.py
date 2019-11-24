from xml_objects.ext.flask import builder

if __name__ == '__main__':
    app = builder.from_args('app.xml')
    app.run(host=app.config['HOST'], port=app.config['PORT'])
