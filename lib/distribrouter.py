'''
Created on 01.10.2014

@author: yfauser
'''
import httplib
import base64
from PyNSXv.lib.xmlformater import CreateXML

class DistribRouter:
    
    def __init__(self,username="admin",password="default",nsx_manager=""):
        self.nsx_manager = nsx_manager
        self.creds= base64.urlsafe_b64encode(username + ':' + password)
        self.headers = {'Content-Type' : 'application/xml','Authorization' : 'Basic ' + self.creds }
    
    def create(self, vdr_name, datacenter_id, vdr_cluster_id, vdr_datastore, vdr_mgmt_pg):
        vdr_appliance_properties = [ {'resourcePoolId': vdr_cluster_id}, {'datastoreId': vdr_datastore}, {'vmHostname': vdr_name} ]
        vdr_appliance = [ {'appliance': vdr_appliance_properties} ]
        vdr_mgmt_interface_properties = [ {'connectedToId': vdr_mgmt_pg} ]
        
        vdr_properties_xml = CreateXML("edge", [ {'datacenterMoid': datacenter_id}, 
                                                {'type': 'distributedRouter'}, 
                                                {'appliances': vdr_appliance}, 
                                                {'mgmtInterface': vdr_mgmt_interface_properties} 
                                                ] 
                                       )
        
        conn = httplib.HTTPSConnection(self.nsx_manager, 443)
        conn.request('POST', 'https://' + self.nsx_manager + '/api/4.0/edges',vdr_properties_xml,self.headers)
        response = conn.getresponse()
        if response.status != 201:
            print str(response.status) + " Services Edge Not created..."
            exit(1)
        else:
            location = response.getheader('location', default=None)
            # The edgeID that is used in later calls to modify edge properties is returned in the location header
            split_result = location.split('/')
            svc_edge_id = split_result[-1]
            return svc_edge_id

        

