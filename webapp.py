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
cherrypy.config.update({'environment': 'embedded'})


if cherrypy.__version__.startswith('3.0') and cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)

def get_list(list_name, params):
    print('get_list list:{} params:{}'.format(str(list_name), str(params)))
    print(db_conf.settings['DB']['db_user'])

    print(db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB']['db_name'])

    return_vals = OrderedDict()

    cnx = mysql.connector.connect(user=db_conf.settings['DB']['db_user'],
                                  password=db_conf.settings['DB']['db_pass'],
                                  host=db_conf.settings['DB']['db_host'],
                                  database=db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB'][
                                      'db_name'])
    cursor = cnx.cursor()

    query = ("SELECT * FROM " + list_name + "_tbl")

    cursor.execute(query)

    query_result = ''
    for (participant_name) in cursor:
        query_result += '\n' + str(participant_name)

    cursor.close()
    cnx.close()

    return_vals['test1'] = 'Hello World' + query_result
    return return_vals


class HoppersWebService(object):
    exposed = True

    def GET(self, *args):
        print('GET:'+str(args))
        if not args:
            args = [None, None]
        if args[0] == 'hoppers' and args[1] == 'rest':
            return json.dumps(get_list(args[2], args[3:]))

    def POST(self, **kwargs):
        return 'POST:/hoppers/' + str(kwargs)

    def PUT(self, **kwargs):
        return 'PUT:/hoppers/' + str(kwargs)

    def DELETE(self, **kwargs):
        return 'DELETE:/hoppers/' + str(kwargs)

    def serve_index(self):
        print('index')
        print(db_conf.settings['static']['path'])
        index_file = os.path.abspath(db_conf.settings['static']['path'] + 'index.html')
        f = open( index_file, 'r' )
        return f.read()

    @cherrypy.expose
    def myfunc(self):
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
                'tools.staticdir.dir': db_conf.settings['static']['path'],
                'tools.staticdir.index': 'index.html',
            }
        }, )
    cherrypy.engine.start()
    cherrypy.engine.block()
