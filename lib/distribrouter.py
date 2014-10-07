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
    
    def enableOSPF(self,edge_id, router_id, protocol_address, forwarding_address, ospf_area, 
                   ospf_vnic_index, ospf_vnic_helloInterval="10", ospf_vnic_deadInterval="40", 
                   ospf_vnic_priority="128", ospf_vnic_cost='none',  ospf_area_type="normal", 
                   authentication_type="none", authentication_password="vmware123", ospf_redist_from_list=None):
        ''' This method is used to configure the OSPF Area and the Interfaces used for/with OSPF
        edge_id: This is the edge id as returned by the create method
        router_id: This is the OSPF Router ID for the OSPF Database, usually this is set to be the same IP as the protocol_adress.
        protocol_address: This is the IP that the VDR uses to source OSPF Hellos, LSRs, etc. Basically this is the IP of the logical router control VM
        forwarding_address: This is the next hop IP for the advertised routes. This is the shared VIP of the VDR in the hypervisor kernel modules
        ospf_area: This is the OSPF Area ID, Mandatory and unique. Valid values are 0-4294967295
        ospf_vnic_index: This is the vnic Index of the VDR Uplink used for OSPF. With the VDR only one Interface can be used as an OSPF Interface. Example: '0'
        ospf_vnic_helloInterval: Optional. Default 10 sec. Valid values are 1-255
        ospf_vnic_deadInterval:  Optional. Default 40 sec. Valid values are 1-65535
        ospf_vnic_priority: Optional. Default 128. Valid values are 0-255
        ospf_vnic_cost: Optional. Auto based on interface speed. Valid values are 1-65535
        ospf_area_type: Optional. Default is normal. Valid inputs are normal, nssa
        authentication_type: Optional. When not specified, its "none" authentication. Valid values are none, password , md5
        authentication_password: Value as per the type of authentication
        ospf_redist_from_list: This is an Optional list of sources to redistribute into OSPF, default is an empty list, 
        accepted values are isis, ospf, bgp, static and connected
        '''
        ospf_interface_config = [{'vnic': ospf_vnic_index}, 
                                 {'areaId': ospf_area}, 
                                 {'helloInterval': ospf_vnic_helloInterval},
                                 {'deadInterval': ospf_vnic_deadInterval},
                                 {'priority': ospf_vnic_priority}]
        if ospf_vnic_cost != 'none': ospf_interface_config.append( {'cost': ospf_vnic_cost} )
        ospf_interfaces = [ {'ospfInterface': ospf_interface_config} ]
        
        routing_global_config = [ {'routerId' : router_id } ]
        
        ospf_authentication_config = [ {'type': authentication_type} ]
        if authentication_type != 'none': ospf_authentication_config.append( {'value': authentication_password} )
        ospf_area_config = [ {'ospfArea': [ {'areaId': ospf_area}, {'type': ospf_area_type}, {'authentication': ospf_authentication_config} ] } ]
        
        if ospf_redist_from_list==None:  ospf_redist_from_list=[]
        if len(ospf_redist_from_list) != 0:
            ospf_redistribution_rules = []
            for redist_from in ospf_redist_from_list:
                ospf_redistribution_rules.append({ redist_from: 'true'})
            ospf_redistribution_property = [{'enabled': 'true'}, {'rules': [ {'rule': [ {'from': ospf_redistribution_rules}, {'action': 'permit'} ] } ] } ]
        else: ospf_redistribution_property = [{'enabled': 'false'}]
        
        ospf_config = [ {'enabled': 'true'}, {'forwardingAddress': forwarding_address}, 
                       {'protocolAddress': protocol_address}, {'ospfAreas': ospf_area_config}, 
                       {'ospfInterfaces': ospf_interfaces}, {'redistribution': ospf_redistribution_property} ]
        
        ospf_prop_xml = CreateXML("routing", [ {'routingGlobalConfig': routing_global_config}, {'ospf': ospf_config} ] )
        
        url='https://' + self.nsx_manager + '/api/4.0/edges/' + edge_id + '/routing/config'
        
        conn = httplib.HTTPSConnection(self.nsx_manager, 443)
        conn.request('PUT', url, ospf_prop_xml, self.headers)
        response = conn.getresponse()
        if response.status != 204:
            print str(response.status) + " OSPF configuration failed..." + str(response.read())
            exit(1)
    
    def staticRoute(self, edge_id, default_gateway=None, default_gateway_vnic_index=None, static_routes_list=None):
        ''' This method configures the static routing table on the services edge, including the defalut gateway if needed
        edge_id: This is the edge id as returned by the create method
        default_gateway: Optional, This is the default gateway IP Address
        default_gateway_vnic_index: Mandatory if default_gateway is set, this is the vnic index (interface) this default gateway points to
        static_routes_list: Optional, This is a list of dictionaries holding the static routes
        static_routes_list dictionary items:
          route_description: Optional: description what this route is for
          route_vnic_index: Mandatory, this is the vnic index (interface) this route points to
          route_network: The prefix in the following notation <prefix>/<prefix length>, e.g. 10.1.1.0/24
          route_nexthop: The routes next hop ip
        '''
        routes_config=[]
        if default_gateway != None: 
            default_route_property=[ {'description': 'default route set by PyNSXv'}, {'vnic': default_gateway_vnic_index}, {'gatewayAddress': default_gateway}, {'mtu': '1500'}]
            routes_config.append( {'defaultRoute': default_route_property} )
        
        if static_routes_list != None:
            static_routes=[]
            for static_route in static_routes_list:
                if 'route_description' not in static_route: static_route['route_description']='route set by PyNSXv'
                static_route_property=[{'description': static_route['route_description']}, {'vnic': static_route['route_vnic_index']}, 
                                       {'network': static_route['route_network']}, {'nextHop': static_route['route_nexthop']}, {'mtu': '1500'}]
                static_routes.append( {'route': static_route_property})
            routes_config.append( {'staticRoutes': static_routes} )
        
        static_routes_xml = CreateXML("staticRouting", routes_config )
        
        url='https://' + self.nsx_manager + '/api/4.0/edges/' + edge_id + '/routing/config/static'
        
        conn = httplib.HTTPSConnection(self.nsx_manager, 443)
        conn.request('PUT', url, static_routes_xml, self.headers)
        response = conn.getresponse()
        if response.status != 204:
            print str(response.status) + " Static Routing configuration failed..." + str(response.read())
            exit(1)
        
    def DHCPrelay(self, edge_id, dhcp_server_list, interface_index_list):
        ''' This method configures the DHCP Relay functionality on the NSX VDR
        NOTE: This feature is only available from NSXv 6.1 onwards
        edge_id: This is the edge id as returned by the create method
        dhcp_server_list: This is a List of DHCP Server to send DHCP requests to
        interface_index_list: This is a list of Interface Indexes were the DHCP Relay functionality should be enabled on
        '''
        dhcp_server_ips = []
        for dhcp_server in dhcp_server_list:
            dhcp_server_ips.append({'ipAddress': dhcp_server})
        
        relay_agents = []
        for relay_agent_vnic_index in interface_index_list:
            relay_agents.append({'relayAgent': [ {'vnicIndex': relay_agent_vnic_index} ] })
        
        dhcp_relay_xml = CreateXML("relay", [{'relayServer': dhcp_server_ips} , {'relayAgents': relay_agents}] )
        print dhcp_relay_xml
        
        url='https://' + self.nsx_manager + '/api/4.0/edges/' + edge_id + '/dhcp/config/relay'
        
        conn = httplib.HTTPSConnection(self.nsx_manager, 443)
        conn.request('PUT', url, dhcp_relay_xml, self.headers)
        response = conn.getresponse()
        if response.status != 204:
            print str(response.status) + " DHCP Relay configuration failed..." + str(response.read())
            exit(1)
        
        
             
        
