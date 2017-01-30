import cherrypy
import json
from collections import OrderedDict
import mysql.connector
import db_conf
import sys
import atexit
import os
import os.path

#sys.stdout = sys.stderr
#cherrypy.config.update({'environment': 'embedded'})


if cherrypy.__version__.startswith('3.0') and cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)

def get_list(list_name, params):
    print('get_list list:{} params:{}'.format(str(list_name), str(params)))
    print(db_conf.settings['DB']['db_user'])

    print(db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB']['db_name'])

    return_vals = []

    cnx = mysql.connector.connect(user=db_conf.settings['DB']['db_user'],
                                  password=db_conf.settings['DB']['db_pass'],
                                  host=db_conf.settings['DB']['db_host'],
                                  database=db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB'][
                                      'db_name'])
    cursor = cnx.cursor(dictionary=True)
    query = ("SELECT * FROM " + list_name + "s_tbl")
    cursor.execute(query)

    for row in cursor:
        return_vals.append(dict(row))
        print(str(row[list_name + '_id']) + ' ' + str(row[list_name + '_name']))

    cursor.close()
    cnx.close()

    print(str(return_vals))

    return return_vals


class HoppersWebService(object):
    exposed = True

    def GET(self, *args):
        print('GET:'+str(args)+cherrypy.request.scheme)
        if not args:
            args = [None, None]
        if args[0] == 'hoppers' and args[1] == 'rest':
            return json.dumps(get_list(args[2], args[3:]) + cherrypy.request.scheme)

    def POST(self, *args):
        print('POST '+str(args)+cherrypy.request.scheme)
        rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        b = json.loads(rawData)
        print('post data: '+str(b))
        return json.dumps('POST:/hoppers/' + str(args) + cherrypy.request.scheme)

    def PUT(self, *args):
        print('PUT ' + str(args)+cherrypy.request.scheme)
        rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        b = json.loads(rawData)
        print('put data: ' + str(b))
        return json.dumps('PUT:/hoppers/' + str(args) + cherrypy.request.scheme)

    def DELETE(self, *args):
        print('DELETE ' + str(args)+cherrypy.request.scheme)
        # rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        # b = json.loads(rawData)
        # print('delete data: ' + str(b))
        return json.dumps('DELETE:/hoppers/' + str(args) + cherrypy.request.scheme)

    def serve_index(self):
        print('index'+cherrypy.request.scheme)
        print(db_conf.settings['static']['path'])
        index_file = os.path.abspath(db_conf.settings['static']['path'] + 'index.html')
        f = open( index_file, 'r' )
        return f.read()

    @cherrypy.expose
    def myfunc(self):
        print('myfunc'++cherrypy.request.scheme)
        return self.serve_index()

if __name__ == '__main__':
    print("name {}".format(db_conf.settings['DB']['db_name']))
    print("user {}".format(db_conf.settings['DB']['db_user']))
    path = None
    cherrypy.tree.mount(
        HoppersWebService(),
        '/',
        {
            '/hoppers/rest': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher()
            },
            '/': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.abspath(db_conf.settings['static']['path']),
                'tools.staticdir.index': 'index.html',
            }
        }, )
    cherrypy.server.ssl_module = 'builtin'
    cherrypy.server.ssl_certificate = "cert.pem"
    cherrypy.server.ssl_private_key = "privkey.pem"
    cherrypy.engine.start()
    cherrypy.engine.block()
