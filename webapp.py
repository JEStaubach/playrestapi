import cherrypy
import os
import json
from collections import OrderedDict
from configparser import ConfigParser
import mysql.connector
import db_conf
import sys
import atexit

#
# import os.path
# import getpass
# from builtins import input


sys.stdout = sys.stderr
cherrypy.config.update({'environment': 'embedded'})


if cherrypy.__version__.startswith('3.0') and cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)


class DBConfig:
    settings = {}

    def __init__(self, config_file='..\db.cfg'):
        if os.path.isfile(config_file):
            config = ConfigParser()
            config.readfp(open(config_file))
            for section in config.sections():
                self.settings[section] = {}
                for option in config.options(section):
                    self.settings[section][option] = config.get(section, option)


def get_list(list_name, params):
    print('get_list list:{} params:{}'.format(str(list_name), str(params)))
    print(db_conf.settings['DB']['db_user'])

    print(db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB']['db_name'])

    return_vals = OrderedDict()

    cnx = mysql.connector.connect(user=db_conf.settings['DB']['db_user'],
                                  password=db_conf.settings['DB']['db_pass'],
                                  host=db_conf.settings['DB']['db_host'],
                                  database=db_conf.settings['DB']['db_user'] + '$' + db_conf.settings['DB']['db_name'])
    cursor = cnx.cursor()

    query = ("SELECT * FROM " + list_name + "_tbl" )


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
        print('GET:/hoppers/'+str(args))
        if not args:
            args = [None]
        return json.dumps(get_list(args[0], args[1:]))

    def POST(self, **kwargs):
        return 'POST:/hoppers/' + str(kwargs)

    def PUT(self, **kwargs):
        return 'PUT:/hoppers/' + str(kwargs)

    def DELETE(self, **kwargs):
        return 'DELETE:/hoppers/' + str(kwargs)

if __name__ == '__main__':
    # db_conf = DBConfig()
    # if not 'DB' in db_conf.settings.keys():
    #     db_conf.settings['DB'] = {}
    # if not 'db_name' in db_conf.settings['DB'].keys():
    #     db_conf.settings['DB']['db_name'] = input('db_name:')
    # if not 'db_user' in db_conf.settings['DB'].keys():
    #     db_conf.settings['DB']['db_user'] = input('db_user:')
    # if not 'db_pass' in db_conf.settings['DB'].keys():
    #     db_conf.settings['DB']['db_pass'] = getpass.getpass('Password:')
    print("name {}".format(db_conf.settings['DB']['db_name']))
    print("user {}".format(db_conf.settings['DB']['db_user']))
    cherrypy.tree.mount(
        HoppersWebService(),
        '/hoppers',
        {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher()
            },
        }, )
    #     cherrypy.tree.mount(
    #         Root(),
    #         '/',
    #         {
    #             '/': {
    #                 'tools.sessions.on': True,
    #                 'tools.staticdir.root': os.path.abspath(os.getcwd())
    #             }
    #         }
    #     )
    cherrypy.engine.start()
    cherrypy.engine.block()
