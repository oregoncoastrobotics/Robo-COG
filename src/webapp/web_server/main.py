import cherrypy
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))

class Root(object):
    def index(self):
	tmpl = env.get_template('index.html')
        return tmpl.render()
    index.exposed = True

if __name__ == '__main__':
   
    cherrypy.config.update(
	{'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(Root())
