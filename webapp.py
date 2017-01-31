import cherrypy
import json
from collections import OrderedDict
import mysql.connector
import db_conf
import sys
import atexit
import os
import os.path
from oauth2client import client, crypt
import urllib2

#sys.stdout = sys.stderr
#cherrypy.config.update({'environment': 'embedded'})

client_id = '105600165694-08orfb5k9o0tit237hnohila4m694ufu.apps.googleusercontent.com'

if cherrypy.__version__.startswith('3.0') and cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)


def get_list(list_name):
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


def signin(in_data):
    print('signin')
    token = in_data['token']
    try:
        idinfo = client.verify_id_token(token, client_id)
        # Or, if multiple clients access the backend server:
        # idinfo = client.verify_id_token(token, None)
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #    raise crypt.AppIdentityError("Unrecognized client.")
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")
            # If auth request is from a G Suite domain:
            # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
            #    raise crypt.AppIdentityError("Wrong hosted domain.")
    except crypt.AppIdentityError:
        # Invalid token
        return {'method': 'post', 'status': 'signin decrypt failed'}
    email = idinfo['email']
    print(email)
    if idinfo['aud'] != client_id:
        return {'method': 'post', 'status': 'signin client id failed'}
    return_vals = []
    cnx = mysql.connector.connect(user=db_conf.settings['DB']['db_user'],
                                  password=db_conf.settings['DB']['db_pass'],
                                  host=db_conf.settings['DB']['db_host'],
                                  database=db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB']['db_name'])
    cursor = cnx.cursor(dictionary=True)
    query = ("SELECT * FROM users WHERE user_email = '" + email + "'")
    cursor.execute(query)
    for row in cursor:
        return_vals.append(dict(row))
    cursor.close()
    cnx.close()
    if len(return_vals) > 0:
        login_succeeded(email)
        return {'method': 'post', 'status': 'success'}
    else:
        login_failed(email)
        return {'method': 'post', 'status': 'signin email not registered'}


def login_failed(email):
    cnx = mysql.connector.connect(user=db_conf.settings['DB']['db_user'],
                                  password=db_conf.settings['DB']['db_pass'],
                                  host=db_conf.settings['DB']['db_host'],
                                  database=db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB']['db_name'])
    cursor = cnx.cursor(dictionary=True)
    query = ("SELECT * FROM failedlogins WHERE failedlogin_email = '" + email + "'")
    cursor.execute(query)
    rows = []
    for row in cursor:
        rows.append(dict(row))
    cursor.close()
    cnx.close()
    fail_count = 1
    fail_id = None
    if len(rows) > 0:
        fail_count = rows[0]['failedlogin_count'] + 1
        fail_id = rows[0]['failedlogin_id']
    cnx = mysql.connector.connect(user=db_conf.settings['DB']['db_user'],
                                  password=db_conf.settings['DB']['db_pass'],
                                  host=db_conf.settings['DB']['db_host'],
                                  database=db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB']['db_name'])
    cursor = cnx.cursor(dictionary=True)
    if fail_count == 1:
        query = "INSERT INTO failedlogins_tbl ( failedlogin_email, failedlogin_count, failedlogin_lastdate, failedlogin_lasttime ) VALUES ( '" + email + "'," + str(fail_count) + ", CURDATE(), CURTIME() )"
    else:
        query = "UPDATE failedlogins_tbl SET failedlogin_count=" + str(fail_count) + ", failedlogin_lastdate=CURDATE(), failedlogin_lasttime=CURTIME() WHERE failedlogin_id = " + str(fail_id)
    cursor.execute(query)
    cursor.close()
    cnx.commit()
    cnx.close()


def login_succeeded(email):
    cnx = mysql.connector.connect(user=db_conf.settings['DB']['db_user'],
                                  password=db_conf.settings['DB']['db_pass'],
                                  host=db_conf.settings['DB']['db_host'],
                                  database=db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB']['db_name'])
    cursor = cnx.cursor(dictionary=True)
    query = "INSERT INTO logins_tbl ( login_email, login_date, login_time ) VALUES ( '" + email + "', CURDATE(), CURTIME() )"
    cursor.execute(query)
    cursor.close()
    cnx.commit()
    cnx.close()


class HoppersWebService(object):
    exposed = True

    def GET(self, *args):
        print('GET:'+str(args)+cherrypy.request.scheme)
        if not args:
            args = [None, None]
        if args[0] == 'hoppers' and args[1] == 'manage':
            return self.manage()
        if args[0] == 'hoppers' and args[1] == 'rest':
            raise cherrypy.HTTPRedirect('/hoppers/manage')

    def POST(self, *args):
        print('POST '+str(args)+cherrypy.request.scheme)
        rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        new_data = json.loads(rawData)
        print('post data: '+str(new_data))
        if args[0] == 'hoppers' and args[1] == 'rest':
            return json.dumps(create_row(new_data, args[2]))
        if args[0] == 'hoppers' and args[1] == 'tokensignin':
            return json.dumps(signin(new_data))

    def PUT(self, *args):
        print('PUT ' + str(args)+cherrypy.request.scheme)
        if args[0] == 'hoppers' and args[1] == 'rest':
            if len(args) > 3:
                rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
                new_data = json.loads(rawData)
                print('put data: ' + str(new_data))
                return json.dumps(update_row(new_data, args[2], args[3:]))
            else:
                # A put without an index treated as a GET
                return json.dumps(get_list(args[2]))

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

    def manage(self):
        index_file = os.path.abspath(db_conf.settings['static']['path'] + 'manage.html')
        f = open( index_file, 'r' )
        return f.read()

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
            '/hoppers/tokensignin': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher()
            },
            '/hoppers/manage': {
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
