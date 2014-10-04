'''
Created on 30.09.2014

@author: yfauser
'''
import urllib2
import base64
from PyNSXv.lib.xmlformater import CreateXML

class LogicalSwitch:
    
    def __init__(self, nsx_manager, username="admin", password="default"):
        self.nsx_manager = nsx_manager
        self.creds= base64.urlsafe_b64encode(username + ':' + password)
        self.headers = {'Content-Type' : 'application/xml','Authorization' : 'Basic ' + self.creds }
    
    def create(self,ls_name,
               ls_description="Created by PyNSXv, description was not set",
               ls_cpmode="UNICAST_MODE", vdn_scope="vdnscope-1"):
        
        url='https://' + self.nsx_manager + '/api/2.0/vdn/scopes/' + vdn_scope + '/virtualwires'
        
        ls_properties_xml = CreateXML("virtualWireCreateSpec",
                                      [{'name': ls_name},
                                       {'description': ls_description},
                                       {'tenantId': "undefined"},
                                       {'controlPlaneMode': ls_cpmode}])
        
        req = urllib2.Request(url=url,data=ls_properties_xml,headers=self.headers)
        response=urllib2.urlopen(req)
        ls_id=response.read()

        return ls_id



    