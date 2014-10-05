'''
Created on 04.10.2014

@author: yfauser
'''
import httplib
import base64
from PyNSXv.lib.xmlformater import CreateXML

class ServicesRouter:
    
    def __init__(self,username="admin",password="default",nsx_manager=""):
        self.nsx_manager = nsx_manager
        self.creds= base64.urlsafe_b64encode(username + ':' + password)
        self.headers = {'Content-Type' : 'application/xml','Authorization' : 'Basic ' + self.creds }
    
    def create(self, esg_name, datacenter_id, esg_cluster_id, esg_datastore, esg_firstif_pg, 
               esg_size="compact", ssh_enabled="false", cli_user="admin", cli_password="default"):
        
        esg_appliance_properties = [ {'resourcePoolId': esg_cluster_id}, {'datastoreId': esg_datastore} ]
        esg_appliance = [ {'applianceSize': esg_size}, {'appliance': esg_appliance_properties} ]
        esg_firstif_properties = [ {'index': '0'}, {'portgroupId': esg_firstif_pg}, {'isConnected': 'True'} ]
        esg_vnics = [ {'vnic': esg_firstif_properties} ]
        cli_settings = [ {'userName': cli_user}, {'password': cli_password}, {'remoteAccess': ssh_enabled}]
        
        esg_properties_xml = CreateXML("edge", [{'datacenterMoid': datacenter_id},
                                                {'name': esg_name},  
                                                {'appliances': esg_appliance}, 
                                                {'vnics': esg_vnics},
                                                {'cliSettings': cli_settings} 
                                                ] 
                                       )
        
        url = 'https://' + self.nsx_manager + '/api/4.0/edges'
        
        conn = httplib.HTTPSConnection(self.nsx_manager, 443)
        conn.request('POST', url, esg_properties_xml, self.headers)
        response = conn.getresponse()
        if response.status != 201:
            print str(response.status) + " Services Edge Not created..." + str(response.read())
            exit(1)
        else:
            location = response.getheader('location', default=None)
            # The edgeID that is used in later calls to modify edge properties is returned in the location header
            split_result = location.split('/')
            svc_edge_id = split_result[-1]
            return svc_edge_id

    def cfgif(self,edge_id, if_index, if_name,ls_id,if_ip,if_mask,if_type):
        ''' edge_id: This is the edge id as returned by the create method
            if_index: This is the edge interface Index. Values are 0..9
            if_name: This is the human readable name set for the Interface
            ls_id: This is the logical switch id (aka vwire und virtual wire ID) as returned by the LogicalSwitch.Create Method
            if_ip: This is the Interface IP Address
            if_mask: This is the Interface Subnet Mask
            if_type: This is the type of Interface in NSX 6.x this can either be 'internal' or 'uplink', 
                     where uplink is the upstream interface e.g. from a NAT perpective
        '''
        
        esg_address_group_property = [ {'primaryAddress': if_ip}, {'subnetMask': if_mask} ]
        esg_address_groups = [ {'addressGroup':  esg_address_group_property} ]
        esg_interface_properties = [{'index': if_index},
                                    {'name': if_name},
                                    {'type': if_type},
                                    {'addressGroups': esg_address_groups},
                                    {'mtu': '1500'}, 
                                    {'isConnected': 'true'},
                                    {'portgroupId': ls_id}]
        
        esg_if_properties_xml = CreateXML("vnics", [{'vnic': esg_interface_properties}])
        
        url='https://' + self.nsx_manager + '/api/4.0/edges/' + edge_id + '/vnics/?action=patch'
        
        conn = httplib.HTTPSConnection(self.nsx_manager, 443)
        conn.request('POST', url, esg_if_properties_xml, self.headers)
        response = conn.getresponse()
        if response.status != 204:
            print str(response.status) + " Interface configuration failed..." + str(response.read())
            exit(1)
    
    def cfgif_list(self, edge_id, if_list):
        # This method is used to configure multiple new interfaces in one shot by passing a list of interfaces containing the Interfaces properties
        esg_interfaces = []
        for interface in if_list:
            esg_address_group_property = [ {'primaryAddress': interface['if_ip']}, {'subnetMask': interface['if_mask']} ]
            esg_address_groups = [ {'addressGroup':  esg_address_group_property} ]
            esg_interface_properties = [{'index': interface['if_index']},
                                        {'name': interface['if_name']},
                                        {'type': interface['if_type']},
                                        {'addressGroups': esg_address_groups},
                                        {'mtu': '1500'}, 
                                        {'isConnected': 'true'},
                                        {'portgroupId': interface['ls_id']}]
            esg_interfaces.append( {'vnic': esg_interface_properties} )
            
        esg_if_properties_xml = CreateXML("vnics", esg_interfaces)
            
        url='https://' + self.nsx_manager + '/api/4.0/edges/' + edge_id + '/vnics/?action=patch'

        conn = httplib.HTTPSConnection(self.nsx_manager, 443)
        conn.request('POST', url, esg_if_properties_xml, self.headers)
        response = conn.getresponse()
        if response.status != 204:
            print str(response.status) + " Interface configuration failed..." + str(response.read())
            exit(1)
    
    def addOSPFArea(self, edge_id, router_id, ospf_area, ospf_area_type="normal", authentication_type="none", authentication_password="vmware123"):
        ''' This method is used to configure the OSPF Areas and with it enabled OSPF on the Edge Services Gateway
        edge_id: This is the edge id as returned by the create method
        router_id: This is the OSPF Router ID for the OSPF Database, usually this is set to be the same IP as one of the Interfaces (e.g. the Backbone Area Interface).
        ospf_area: This is the OSPF Area ID, Mandatory and unique. Valid values are 0-4294967295
        ospf_area_type: Optional. Default is normal. Valid inputs are normal, nssa
        authentication_type: Optional. When not specified, its "none" authentication. Valid values are none, password , md5
        authentication_password: Value as per the type of authentication
        '''
        routing_global_config = [ {'routerId' : router_id } ]
        ospf_authentication_config = [ {'type': authentication_type} ]
        if authentication_type != 'none': ospf_authentication_config.append( {'value': authentication_password} )
        
        ospf_area_config = [ {'ospfArea': [ {'areaId': ospf_area}, {'type': ospf_area_type}, {'authentication': ospf_authentication_config} ] } ]
        ospf_config = [ {'enabled': 'true'}, {'ospfAreas': ospf_area_config} ]
        
        ospf_prop_xml = CreateXML("routing", [ {'routingGlobalConfig': routing_global_config}, {'ospf': ospf_config} ] )
        
        url='https://' + self.nsx_manager + '/api/4.0/edges/' + edge_id + '/routing/config'
        
        conn = httplib.HTTPSConnection(self.nsx_manager, 443)
        conn.request('PUT', url, ospf_prop_xml, self.headers)
        response = conn.getresponse()
        if response.status != 204:
            print str(response.status) + " OSPF configuration failed..." + str(response.read())
            exit(1)
    
    def addOSPFArealist(self, edge_id, router_id, ospf_area_list):
        #This method is used to configure multiple OSPF Areas with one method call by supplying a list of dictionaries containing Area definitions
        routing_global_config = [ {'routerId' : router_id } ]
        ospf_areas = []
        for ospf_area in ospf_area_list:
            if ('authentication_type') not in ospf_area: ospf_area['authentication_type'] = 'none'
            if ('ospf_area_type') not in ospf_area: ospf_area['ospf_area_type'] = 'normal'
            ospf_authentication_config = [ {'type': ospf_area['authentication_type']} ]
            if ospf_area['authentication_type'] != 'none': ospf_authentication_config.append( {'value': ospf_area['authentication_password'] } )
            ospf_areas.append( {'ospfArea': [ {'areaId': ospf_area['ospf_area']}, {'type': ospf_area['ospf_area_type']}, {'authentication': ospf_authentication_config} ] } )
        
        ospf_config = [ {'enabled': 'true'}, {'ospfAreas': ospf_areas} ]
        
        ospf_prop_xml = CreateXML("routing", [ {'routingGlobalConfig': routing_global_config}, {'ospf': ospf_config} ] )
        
        url='https://' + self.nsx_manager + '/api/4.0/edges/' + edge_id + '/routing/config'
        
        conn = httplib.HTTPSConnection(self.nsx_manager, 443)
        conn.request('PUT', url, ospf_prop_xml, self.headers)
        response = conn.getresponse()
        if response.status != 204:
            print str(response.status) + " OSPF configuration failed..." + str(response.read())
            exit(1)