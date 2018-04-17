#!/usr/bin/python
import cherrypy
from mako.template import Template
import traceback
import logging
import os
import json

class BcbusWeb(object):
    def __init__(self, config):
        self._config = config
        
        template_dir = os.path.join(config["BCLAB_ROOT"], 'web', 'template')
        templates = os.listdir(template_dir)
        logging.info('serving:')
        logging.info(templates)

        for t in templates:
            def inner(self, template_file=t):
                try:
                    filename = os.path.join(template_dir, template_file)
                    template = Template(filename=filename)
                    return template.render(**self._config)
                except:
                    logging.error(traceback.format_exc())
                    raise
            
            name = t[:-5]
            setattr(self.__class__, name, inner)
            setattr(inner, 'exposed', True)


def main():
    print((__file__ + " running"))

    logging.getLogger().setLevel(logging.INFO)
    with open('webserver.json') as json_file:
        cfg = json.load(json_file)
    logging.info(cfg)
    
    cfg["BCLAB_ROOT"] = os.path.join(os.getcwd(), '..')

    cherrypy_cfg = {
        'global': {
            'server.socket_host': cfg["BCLAB_HOST"],
            'server.socket_port': cfg["WEB_PORT"],
            'server.thread_pool': 8
        },
        '/': { 'tools.staticdir.root': cfg["BCLAB_ROOT"]},

        '/web': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'web'
        },
        '/js': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'web/js'
        }
    }
    logging.info(cherrypy_cfg)

    try:
        cherrypy.quickstart(BcbusWeb(cfg), '/', cherrypy_cfg)
    except:
        log.error(traceback.format_exc())

if __name__ == "__main__":
    main()