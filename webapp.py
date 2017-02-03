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
from urlparse import urlparse

#sys.stdout = sys.stderr
#cherrypy.config.update({'environment': 'embedded'})

client_id = '105600165694-08orfb5k9o0tit237hnohila4m694ufu.apps.googleusercontent.com'

if cherrypy.__version__.startswith('3.0') and cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)


def get_list(args):
    list_name = args[0]
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


def remove_row(args):
    list_name = args[0]
    id = args[1]
    cnx = mysql.connector.connect(user=db_conf.settings['DB']['db_user'],
                                  password=db_conf.settings['DB']['db_pass'],
                                  host=db_conf.settings['DB']['db_host'],
                                  database=db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB']['db_name'])
    cursor = cnx.cursor(dictionary=True)
    cmd = "DELETE FROM " + list_name + "_tbl WHERE " + list_name + "_tbl." + list_name[:-1] + "_id = " + id
    query = cmd
    cursor.execute(query)
    cursor.close()
    cnx.commit()
    cnx.close()
    return {'method': 'DELETE', 'status': 'success'}


def create_row(args):
    new_data = args[0]
    list_name = args[1]
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
    return {'method': 'POST', 'status': 'success'}


def update_row(args):
    new_data = args[0]
    list_name = args[1]
    id = args[2]
    cnx = mysql.connector.connect(user=db_conf.settings['DB']['db_user'],
                                  password=db_conf.settings['DB']['db_pass'],
                                  host=db_conf.settings['DB']['db_host'],
                                  database=db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB']['db_name'])
    cursor = cnx.cursor(dictionary=True)
    cmd = "UPDATE " + list_name + "_tbl SET " + ','.join([key + " = '" + new_data[key] + "'" for key in new_data.keys()]) + " WHERE " + list_name + "_tbl." + list_name[:-1] + "_id = " + id
    print(cmd)
    query = cmd
    cursor.execute(query)
    cursor.close()
    cnx.commit()
    cnx.close()
    return {'method': 'UPDATE', 'status': 'success'}


def verify(token):
    print('signin')
    try:
        idinfo = client.verify_id_token(token, None)
        if idinfo['aud'] not in [client_id]:
           raise crypt.AppIdentityError("Unrecognized client.")
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")
    except crypt.AppIdentityError:
        return {'status': 'token validation failed'}
    email = idinfo['email']
    print(email)
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
        return {'status': 'success', 'permissions': return_vals[0]['user_permissions']}
    else:
        login_failed(email)
        return {'status': 'user not registered'}


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
    exposed_views = {}

    def __init__(self):
        print('init called')
        self.get_exposed_views()
        print(str(self.exposed_views))

    def get_exposed_views(self):
        cnx = mysql.connector.connect(user=db_conf.settings['DB']['db_user'],
                                      password=db_conf.settings['DB']['db_pass'],
                                      host=db_conf.settings['DB']['db_host'],
                                      database=db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB'][
                                          'db_name'])
        cursor = cnx.cursor(dictionary=True)
        query = ("SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME IN (SELECT exposedview_name FROM exposedviews)")
        cursor.execute(query)
        self.exposed_views = {}
        for row in cursor:
            row_dict = dict(row)
            if row_dict['TABLE_NAME'] not in self.exposed_views.keys():
                self.exposed_views[str(row_dict['TABLE_NAME'])] = []
            self.exposed_views[str(row_dict['TABLE_NAME'])].append({'column_name': row_dict['COLUMN_NAME'],
                                                                    'column_type': row_dict['DATA_TYPE']})
        cursor.close()
        cnx.close()

    def unhandled(self, method, url, args):
        cherrypy.response.status = 404
        return json.dumps({'method': method,
                           'resource': url,
                           'status': 'Unhandled resource location ' + str(args)})

    def bad_fields(self, method, url, args, field_errors):
        cherrypy.response.status = 400
        return json.dumps({'method': method,
                           'resource': url,
                           'status': 'Unknown resource attributes: ' + str(field_errors)})

    def collection_exposed(self, collection):
        if collection in self.exposed_views.keys():
            return True
        else:
            return False

    def field_mismatches(self, collection, new_data):
        allowed_fields = [x['column_name'] for x in self.exposed_views[collection]]
        print('collection: ' + collection)
        print('allowed_fields: ' + str(allowed_fields))
        additional_supplied_fields = [x for x in new_data.keys() if x not in allowed_fields]
        unsupplied_fields = [x for x in allowed_fields if x not in new_data.keys() and x != collection[:-1] + '_id']
        tables_with_unsupplied_ids = [x[:-3] for x in unsupplied_fields if x[-3:] == '_id']
        missing_fields = []
        for table in tables_with_unsupplied_ids:
            for field in new_data.keys():
                if table in field:
                    missing_fields.append(table + '_id')
        return {'additional_supplied_fields': additional_supplied_fields,
                'unsupplied_fields': unsupplied_fields,
                'missing_fields': missing_fields}

    def check_token(self, token, method, url, cb, args):
        if not token:
            # token required in order to be verified
            cherrypy.response.status = 401
            return json.dumps({'method': method,
                               'resource': url,
                               'status': 'missing token'})
        else:
            crud = {'POST':   'C',
                    'GET':    'R',
                    'PUT':    'U',
                    'DELETE': 'D',}
            authorization = verify(token)
            if authorization['status'] == 'success':
                # token is authentic and user is registered.
                if crud[method] in authorization['permissions']:
                    # user has required permissions
                    return json.dumps(cb(args))
                else:
                    # User lacks READ permissions
                    cherrypy.response.status = 403
                    return json.dumps({'method': method,
                                       'resource': url,
                                      'status': 'Insufficient privileges'})
            elif authorization['status'] == 'token validation failed':
                # bad token.
                cherrypy.response.status = 401
                cherrypy.response.headers['Location'] = url
                return json.dumps({'method': method,
                                   'resource': url,
                                   'status': authorization['status']})
            elif authorization['status'] == 'user not registered':
                # token OK, but user not registered.
                cherrypy.response.status = 401
                cherrypy.response.headers['Location'] = url
                return json.dumps({'method': method,
                                   'resource': url,
                                   'status': authorization['status']})
            else:
                # token verification - unhandled response
                cherrypy.response.status = 401
                cherrypy.response.headers['Location'] = url
                return json.dumps({'method': method,
                                   'resource': url,
                                   'status': authorization['status']})

    def GET(self, *args, **kwargs):
        print('GET:'+str(args)+cherrypy.request.scheme)
        token = cherrypy.request.headers.get('Authorization')
        url = urlparse(cherrypy.url()).path
        if not args:
            args = [None, None]
        if args[0] == 'hoppers' and args[1] == 'manage':
            return self.manage()
        elif args[0] == 'hoppers' and args[1] == 'rest':
            if not token:
                # Attempt to access a resource or collection without including token.
                # Redirect to login page, pass along the requested URL in Location header.
                cherrypy.response.headers['Location'] = url
                raise cherrypy.HTTPRedirect("/hoppers/manage/#/" + args[2])
            else:
                if not self.collection_exposed(args[2]):
                    return self.unhandled('GET', url, args[2:])
                return self.check_token(token, 'GET', url, get_list, args[2:])
        elif args[0] == 'hoppers' and args[1] == 'tokensignin':
            def on_success(args=None):
                return json.dumps({'method': 'GET',
                                   'resource': url,
                                   'status': 'success',})
            return self.check_token(token, 'GET', url, on_success, None)
        else:
            return self.unhandled('GET', url, args)

    def POST(self, *args):
        print('POST '+str(args)+cherrypy.request.scheme)
        token = cherrypy.request.headers.get('Authorization')
        url = urlparse(cherrypy.url()).path
        rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        new_data = json.loads(rawData)
        print('post data: '+str(new_data))
        if args[0] == 'hoppers' and args[1] == 'rest':
            if not self.collection_exposed(args[2]):
                return self.unhandled('POST', url, args[2:])
            field_errors = self.field_mismatches(args[2], new_data)
            if field_errors['additional_supplied_fields'] or field_errors['unsupplied_fields']:
                return self.bad_fields('POST', url, args[2:], field_errors)
            return self.check_token(token, 'POST', url, create_row, [new_data] + list(args[2:]))
        else:
            return self.unhandled('POST', url, args)

    def PUT(self, *args):
        print('PUT ' + str(args)+cherrypy.request.scheme)
        token = cherrypy.request.headers.get('Authorization')
        url = urlparse(cherrypy.url()).path
        rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        new_data = json.loads(rawData)
        print('put data: ' + str(new_data))
        if args[0] == 'hoppers' and args[1] == 'rest':
            if not self.collection_exposed(args[2]):
                return self.unhandled('PUT', url, args[2:])
            field_errors = self.field_mismatches(args[2], new_data)
            if field_errors['additional_supplied_fields'] or field_errors['missing_fields']:
                return self.bad_fields('PUT', url, args[2:], field_errors)
            return self.check_token(token, 'PUT', url, update_row, [new_data] + list(args[2:]))
        else:
            return self.unhandled('PUT', url, args)

    def DELETE(self, *args):
        print('DELETE ' + str(args)+cherrypy.request.scheme)
        token = cherrypy.request.headers.get('Authorization')
        url = urlparse(cherrypy.url()).path
        #rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        #new_data = json.loads(rawData)
        #print('delete data: ' + str(new_data))
        if args[0] == 'hoppers' and args[1] == 'rest':
            if not self.collection_exposed(args[2]):
                return self.unhandled('DELETE', url, args[2:])
            return self.check_token(token, 'DELETE', url, remove_row, args[2:])
        else:
            return self.unhandled('DELETE', url, args)

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
