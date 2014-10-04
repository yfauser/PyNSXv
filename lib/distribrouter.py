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
    
    def create(self, datacenter_id, vdr_cluster_id, vdr_datastore, vdr_mgmt_pg):
        vdr_appliance_properties = [ {'resourcePoolId': vdr_cluster_id}, {'datastoreId': vdr_datastore} ]
        vdr_appliance = [ {'appliance': vdr_appliance_properties} ]
        vdr_mgmt_interface_properties = [ {'connectedToId': vdr_mgmt_pg} ]
        
        vdr_properties_xml = CreateXML("edge", [ {'datacenterMoid': datacenter_id}, 
                                                {'type': 'distributedRouter'}, 
                                                {'appliances': vdr_appliance}, 
                                                {'mgmtInterface': vdr_mgmt_interface_properties} 
                                                ] 
                                       )
        
        url = 'https://' + self.nsx_manager + '/api/4.0/edges'
        
        conn = httplib.HTTPSConnection(self.nsx_manager, 443)
        conn.request('POST', url, vdr_properties_xml, self.headers)
        response = conn.getresponse()
        if response.status != 201:
            print str(response.status) + " Services Edge Not created..."  + str(response.read())
            exit(1)
        else:
            location = response.getheader('location', default=None)
            # The edgeID that is used in later calls to modify edge properties is returned in the location header
            split_result = location.split('/')
            vdr_edge_id = split_result[-1]
            return vdr_edge_id

    def addif(self,edge_id,if_name,ls_id,if_ip,if_mask,if_type):
        ''' edge_id: This is the edge id as returned by the create method
            if_name: This is the human readable name set for the Interface
            ls_id: This is the logical switch id (aka vwire und virtual wire ID) as returned by the LogicalSwitch.Create Method
            if_ip: This is the Interface IP Address
            if_mask: This is the Interface Subnet Mask
            if_type: This is the type of Interface in NSX 6.x this can either be 'internal' or 'uplink', 
                     where uplink is the upstream interface that can have dynamic routing applied
        '''
        
        vdr_address_group_property = [ {'primaryAddress': if_ip}, {'subnetMask': if_mask} ]
        vdr_address_groups = [ {'addressGroup':  vdr_address_group_property} ]
        vdr_interface_properties = [{'name': if_name}, 
                                    {'addressGroups': vdr_address_groups},
                                    {'mtu': '1500'},
                                    {'type': if_type}, 
                                    {'isConnected': 'true'},
                                    {'connectedToId': ls_id},]
        
        vdr_if_properties_xml = CreateXML("interfaces", [{'interface': vdr_interface_properties}])
        
        url='https://' + self.nsx_manager + '/api/4.0/edges/' + edge_id + '/interfaces/?action=patch'
        
        conn = httplib.HTTPSConnection(self.nsx_manager, 443)
        conn.request('POST', url, vdr_if_properties_xml, self.headers)
        response = conn.getresponse()
        if response.status != 200:
            print str(response.status) + " Interface configuration failed..." + str(response.read())
            exit(1)

    
    def addif_list(self, edge_id, if_list):
        # This method is used to configure multiple new interfaces in one shot by passing a list of interfaces containing the Interfaces properties
        vdr_interfaces = []
        for interface in if_list:
            vdr_address_group_property = [ {'primaryAddress': interface['if_ip']}, {'subnetMask': interface['if_mask']} ]
            vdr_address_groups = [ {'addressGroup':  vdr_address_group_property} ]
            vdr_interface_properties = [{'name': interface['if_name']}, 
                                        {'addressGroups': vdr_address_groups},
                                        {'mtu': '1500'},
                                        {'type': interface['if_type']}, 
                                        {'isConnected': 'true'},
                                        {'connectedToId': interface['ls_id']},]
            vdr_interfaces.append( {'interface': vdr_interface_properties} )
            
        vdr_if_properties_xml = CreateXML("interfaces", vdr_interfaces)
            
        url='https://' + self.nsx_manager + '/api/4.0/edges/' + edge_id + '/interfaces/?action=patch'
        
        conn = httplib.HTTPSConnection(self.nsx_manager, 443)
        conn.request('POST', url, vdr_if_properties_xml, self.headers)
        response = conn.getresponse()
        if response.status != 200:
            print str(response.status) + " Interface configuration failed..." + str(response.read())
            exit(1)

