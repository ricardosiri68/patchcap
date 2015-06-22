import xmlrpclib
import logging
import ConfigParser

class SuperControl(object):
	def __init__(self):
        	config = ConfigParser.ConfigParser()
        	config.read("/etc/supervisord.conf")
        	u = config.get('inet_http_server', 'username')
        	p = config.get('inet_http_server', 'password')
 		self.server = xmlrpclib.Server('http://%s:%s@localhost:9002/RPC2'%(u, p))
	
	def restart(self, group):
		logging.debug('restarting process'+group)
		print self.server.supervisor.stopProcessGroup(group)
		print self.server.supervisor.startProcessGroup(group)

	
	def state(self, name):
		return self.server.supervisor.getProcessInfo(name)

if __name__ == "__main__": 
	s = SuperControl()

	state = s.state('condor:condor-0')
	print state['start']
	print state['statename']
	print state['pid']

