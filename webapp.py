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
    return_vals = []
    cnx = mysql.connector.connect(user=db_conf.settings['DB']['db_user'],
                                  password=db_conf.settings['DB']['db_pass'],
                                  host=db_conf.settings['DB']['db_host'],
                                  database=db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB']['db_name'])
    cursor = cnx.cursor(dictionary=True)
    query = ("SELECT * FROM " + list_name)
    cursor.execute(query)
    for row in cursor:
        return_vals.append(dict(row))
    cursor.close()
    cnx.close()
    return return_vals


def remove_row(list_name, params):
    cnx = mysql.connector.connect(user=db_conf.settings['DB']['db_user'],
                                  password=db_conf.settings['DB']['db_pass'],
                                  host=db_conf.settings['DB']['db_host'],
                                  database=db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB']['db_name'])
    cursor = cnx.cursor(dictionary=True)
    cmd = "DELETE FROM " + list_name + "_tbl WHERE " + list_name + "_tbl." + list_name[:-1] + "_id = " + params[0]
    query = cmd
    cursor.execute(query)
    cursor.close()
    cnx.commit()
    cnx.close()
    return {'method': 'delete', 'status': 'success'}


def create_row(new_data, list_name):
    cnx = mysql.connector.connect(user=db_conf.settings['DB']['db_user'],
                                  password=db_conf.settings['DB']['db_pass'],
                                  host=db_conf.settings['DB']['db_host'],
                                  database=db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB']['db_name'])
    cursor = cnx.cursor(dictionary=True)
    cmd = "INSERT INTO " + list_name + "_tbl (" + ",".join(new_data.keys())+") VALUES (" + ",".join([ "'" + new_data[key] + "'" for key in new_data]) + ")"
    query = cmd
    cursor.execute(query)
    cursor.close()
    cnx.commit()
    cnx.close()
    return {'method': 'post', 'status': 'success'}


def update_row(new_data, list_name, params):
    cnx = mysql.connector.connect(user=db_conf.settings['DB']['db_user'],
                                  password=db_conf.settings['DB']['db_pass'],
                                  host=db_conf.settings['DB']['db_host'],
                                  database=db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB']['db_name'])
    cursor = cnx.cursor(dictionary=True)
    cmd = "UPDATE " + list_name + "_tbl SET " + ','.join([key + " = '" + new_data[key] + "'" for key in new_data.keys()]) + " WHERE " + list_name + "_tbl." + list_name[:-1] + "_id = " + params[0]
    print(cmd)
    query = cmd
    cursor.execute(query)
    cursor.close()
    cnx.commit()
    cnx.close()
    return {'method': 'delete', 'status': 'success'}



class HoppersWebService(object):
    exposed = True

    def GET(self, *args):
        print('GET:'+str(args)+cherrypy.request.scheme)
        if not args:
            args = [None, None]
        if args[0] == 'hoppers' and args[1] == 'rest':
            return json.dumps(get_list(args[2], args[3:]))

    def POST(self, *args):
        print('POST '+str(args)+cherrypy.request.scheme)
        rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        new_data = json.loads(rawData)
        print('post data: '+str(new_data))
        if args[0] == 'hoppers' and args[1] == 'rest':
            return json.dumps(create_row(new_data, args[2]))

    def PUT(self, *args):
        print('PUT ' + str(args)+cherrypy.request.scheme)
        rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        new_data = json.loads(rawData)
        print('put data: ' + str(new_data))
        if args[0] == 'hoppers' and args[1] == 'rest':
            return json.dumps(update_row(new_data, args[2], args[3:]))

    def DELETE(self, *args):
        print('DELETE ' + str(args)+cherrypy.request.scheme)
        if args[0] == 'hoppers' and args[1] == 'rest':
            return json.dumps(remove_row(args[2], args[3:]))

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
