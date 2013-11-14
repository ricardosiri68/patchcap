from suds.client import Client
import hmac, hashlib
import base64
from patchman.utils.wsdiscovery import *
import binascii
import logging

from suds.client import Client 
from suds.wsse import Security
from suds_passworddigest.token import UsernameDigestToken

def toascii(p):
    return p.encode('hex').upper()#''.join(str(ord(c)) for c in p)


logging.basicConfig(filename="suds.log", level=logging.DEBUG)
logging.getLogger('suds.client').setLevel(logging.INFO)
logging.getLogger('suds.transport').setLevel(logging.WARNING)
logging.getLogger('suds.xsd.schema').setLevel(logging.WARNING)
logging.getLogger('suds.wsdl').setLevel(logging.WARNING)

wsd = WSDiscovery()
wsd.start()
#typeNVT = QName("http://www.onvif.org/ver10/network/wsdl","NetworkVideoTransmitter");
#ret = wsd.searchServices(types=[typeNVT])
ret = wsd.searchServices()
for service in ret:
    print "Device: " + service.getEPR() + ":"
    print "Address information: " + str(service.getXAddrs())
    print "Scopes: " + str(service.getScopes())

service = ret[0]
uri =  service.getXAddrs()[0]
urn = service.getEPR()
wsd.stop()

uri = 'http://192.168.3.20/onvif/services'
urn = 'uuid:76931fac-9dab-2b36-c248-a8556a00bec4'

u = 'root'
p = 'root'

op='ONVIF password'

#test sample
#urn = 'uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6'
#u = 'user'
#p ='VRxuNzpqrX' 

nep = urn[5:].replace('-','').upper()

nep_op=nep+toascii(op)
u_p  = u+p
digest =hmac.new(u_p, nep_op.decode('hex'), hashlib.sha1).digest()
user_pass = base64.b64encode(digest)

security = Security()
token = UsernameDigestToken(u, p)
#token.setnonce()
#token.setcreated()
security.tokens.append(token) 
#client.set_options(wsse=security)


from suds.bindings import binding
binding.envns=('SOAP-ENV', 'http://www.w3.org/2003/05/soap-envelope')

wsdl_url = 'file:///home/hernando/proyectos/patchcap/cam/onvif/def/devicemgmt_1.wsdl'
#wsdl_url ='http://www.onvif.org/onvif/ver10/device/wsdl/devicemgmt.wsdl' 
client = Client(wsdl_url,location=uri, wsse=security)
#print client
#print client.service.GetHostname()
print client.service.GetSystemDateAndTime()
#print client.service.GetDeviceInformation()
#print client.service.GetRelayOutputs()
#print client.service.GetCapabilities('All')
#client.last_sent()
#client.last_received()



