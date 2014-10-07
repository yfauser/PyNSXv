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
    
        
    def enableOSPF(self, edge_id, router_id, ospf_area_list, ospf_interface_list, ospf_redist_from_list=None):
        # TODO: At some point it would also be good to have the ability to set prefix filters for the redistribution
        ''' This method is used to configure the OSPF Areas, Interfaces, and with it enabled OSPF on the Edge Services Gateway
        edge_id: This is the edge id as returned by the create method
        ospf_area_list: This is a List of Dictionaries containing OSPF Area definitions and their properties
        ospf_interface_list: This is a list of Dictionaries containing OSPF Interfaces and their Timers
        ospf_area_list properties set in the dictionaries:
          ospf_area: This is the OSPF Area ID, Mandatory and unique. Valid values are 0-4294967295
          ospf_area_type: Optional. Default is normal. Valid inputs are normal, nssa
          authentication_type: Optional. When not specified, its "none" authentication. Valid values are none, password , md5
          authentication_password: Value as per the type of authentication
        ospf_interface_list properties set in the dictionaries:  
          vnic_index: This is the vnic Index of the VDR Uplink used for OSPF. With the VDR only one Interface can be used as an OSPF Interface. Example: '0'
          helloInterval: Optional. Default 10 sec. Valid values are 1-255
          deadInterval:  Optional. Default 40 sec. Valid values are 1-65535
          priority: Optional. Default 128. Valid values are 0-255
          cost: Optional. Auto based on interface speed. Valid values are 1-65535
        ospf_redist_from_list: This is an Optional list of sources to redistribute into OSPF, default is an empty list, 
        accepted values are isis, ospf, bgp, static and connected
        '''
        routing_global_config = [ {'routerId' : router_id } ]
        
        ospf_areas = []
        for ospf_area in ospf_area_list:
            if ('authentication_type') not in ospf_area: ospf_area['authentication_type'] = 'none'
            if ('ospf_area_type') not in ospf_area: ospf_area['ospf_area_type'] = 'normal'
            ospf_authentication_config = [ {'type': ospf_area['authentication_type']} ]
            if ospf_area['authentication_type'] != 'none': ospf_authentication_config.append( {'value': ospf_area['authentication_password'] } )
            ospf_areas.append( {'ospfArea': [ {'areaId': ospf_area['ospf_area']}, {'type': ospf_area['ospf_area_type']}, {'authentication': ospf_authentication_config} ] } )
        
        ospf_interfaces = []
        for interface in ospf_interface_list:
            if ('helloInterval') not in interface: interface['helloInterval']= '10'
            if ('deadInterval') not in interface: interface['deadInterval']= '40'
            if ('priority') not in interface: interface['priority']= '128'
            if ('cost') not in interface: interface['cost']= None
            ospf_interface_config = [{'vnic': interface['vnic_index']}, 
                                     {'areaId': interface['ospf_area']}, 
                                     {'helloInterval': interface['helloInterval']},
                                     {'deadInterval': interface['deadInterval']},
                                     {'priority': interface['priority']}]
            if interface['cost'] != None: ospf_interface_config.append( {'cost': interface['cost'] } )
            ospf_interfaces.append( {'ospfInterface': ospf_interface_config} )
        
        if ospf_redist_from_list==None:  ospf_redist_from_list=[]
        if len(ospf_redist_from_list) != 0:
            ospf_redistribution_rules = []
            for redist_from in ospf_redist_from_list:
                ospf_redistribution_rules.append({ redist_from: 'true'})
            ospf_redistribution_property = [{'enabled': 'true'}, {'rules': [ {'rule': [ {'from': ospf_redistribution_rules}, {'action': 'permit'} ] } ] } ]
        else: ospf_redistribution_property = [{'enabled': 'false'}]
            
        ospf_config = [ {'enabled': 'true'}, {'ospfAreas': ospf_areas}, {'ospfInterfaces': ospf_interfaces}, {'redistribution': ospf_redistribution_property}]
        
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
        ''' This method configures the DHCP Relay functionality on the NSX Edge Services Gateway
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
        
        url='https://' + self.nsx_manager + '/api/4.0/edges/' + edge_id + '/dhcp/config/relay'
        
        conn = httplib.HTTPSConnection(self.nsx_manager, 443)
        conn.request('PUT', url, dhcp_relay_xml, self.headers)
        response = conn.getresponse()
        if response.status != 204:
            print str(response.status) + " DHCP Relay configuration failed..." + str(response.read())
            exit(1)
    
    def DHCPServer(self, edge_id, static_binding_dict_list=None, ip_pools_dict_list=None):
        ''' This method configures the DHCP Server functionality on the NSX Edge Services Gateway
        edge_id: This is the edge id as returned by the create method
        static_binding_dict_list: This is a list containing dictionaries containing the static entry properties
        ip_pools_dict_list: This is a list containing dictionaries containing the IP Pool configurations
        static_binding_dict_list dictionary values:
          mac_address: Optional - This binds the IP to a specific MAC Address. 
                                 The entry can also be specified with the vmId and vnicId as found in vCenter
          vm_id: Optional - The vm must be connected to the given vNic below.
          vm_vnic_id: Optional - This is the vNic Id of the VM's interface this static DHCP entry is bound to
          hostname: Required- Hostname returned to the Host by DHCP
          ip_address: Required - The static IP Address to give to the VM
          default_gateway: Optional - If not set, this will return to the edge vnics primary IP to the client via DHCP
          domain_name: Optional - DNS Domain Name returned to the Host by DHCP
          primary_ns: Optional - if autoConfigDNS=true, the DNS primary/secondary ips will be generated from DNS service(if configured)
          secondary_ns: - Optional, see above
          lease_time: Optional - in second, default is "86400". valid leaseTime is a valid digit, or "infinite" 
          auto_config_dns: Optional - Defaults to true
        ip_pools_dict_list dictionary values:
          ip_range: required. the ipRange must belongs to one of a subnet of Edge vNics. 
                    And can NOT contain any ip that defined explicitly as vNic primary ip or secondary ip
          default_gateway: Optional - If not set, this will return to the edge vnics primary IP to the client via DHCP
          domain_name: Optional - DNS Domain Name returned to the Host by DHCP
          primary_ns: Optional - if autoConfigDNS=true, the DNS primary/secondary ips will be generated from DNS service(if configured)
          secondary_ns - Optional, see above
          lease_time: Optional - in second, default is "86400". valid leaseTime is a valid digit, or "infinite" 
          auto_config_dns: Optional - Defaults to true
        '''
        dhcp_server_config = [{'enabled': 'true'}]
        static_bindings_list=[]
        ip_pool_list=[]
        if static_binding_dict_list != None:
            property_keys = ['mac_address','vm_id','vm_vnic_id','default_gateway','domain_name','primary_ns','secondary_ns','lease_time','auto_config_dns']
            for static_binding_dict in static_binding_dict_list:
                static_binding_properties=[]
                for property_key in property_keys:
                    if (property_key) not in static_binding_dict: static_binding_dict[property_key]=None
                
                if static_binding_dict['mac_address'] != None: 
                    static_binding_properties.append({'macAddress': static_binding_dict['mac_address']})
                else:
                    if static_binding_dict['vm_id'] != None: static_binding_properties.append({'vmId': static_binding_dict['vm_id']})
                    if static_binding_dict['vm_vnic_id'] != None: static_binding_properties.append({'vnicId': static_binding_dict['vm_vnic_id']})
                
                static_binding_properties.append({'hostname': static_binding_dict['hostname']})
                static_binding_properties.append({'ipAddress': static_binding_dict['ip_address']})
                if static_binding_dict['default_gateway'] != None: static_binding_properties.append({'defaultGateway': static_binding_dict['default_gateway']})
                if static_binding_dict['domain_name'] != None: static_binding_properties.append({'domainName': static_binding_dict['domain_name']})
                if static_binding_dict['primary_ns'] != None: static_binding_properties.append({'primaryNameServer': static_binding_dict['primary_ns']})
                if static_binding_dict['secondary_ns'] != None: static_binding_properties.append({'secondaryNameServer': static_binding_dict['secondary_ns']})
                if static_binding_dict['lease_time'] != None: static_binding_properties.append({'leaseTime': static_binding_dict['lease_time']})
                if static_binding_dict['auto_config_dns'] != None: static_binding_properties.append({'autoConfigureDNS': static_binding_dict['auto_config_dns']})
            
                static_bindings_list.append({'staticBinding': static_binding_properties})
            
            dhcp_server_config.append({'staticBindings': static_bindings_list})
            
        if ip_pools_dict_list != None:
            property_keys = ['default_gateway','domain_name','primary_ns','secondary_ns','lease_time','auto_config_dns']
            for ip_pools_dict in ip_pools_dict_list:
                ip_pool_properties=[]
                for property_key in property_keys:
                    if (property_key) not in ip_pools_dict: ip_pools_dict[property_key]=None
                
                ip_pool_properties.append({'ipRange': ip_pools_dict['ip_range']})
                if ip_pools_dict['default_gateway'] != None: ip_pool_properties.append({'defaultGateway': ip_pools_dict['default_gateway']})
                if ip_pools_dict['domain_name'] != None: ip_pool_properties.append({'domainName': ip_pools_dict['domain_name']})
                if ip_pools_dict['primary_ns'] != None: ip_pool_properties.append({'primaryNameServer': ip_pools_dict['primary_ns']})
                if ip_pools_dict['secondary_ns'] != None: ip_pool_properties.append({'secondaryNameServer': ip_pools_dict['secondary_ns']})
                if ip_pools_dict['lease_time'] != None: ip_pool_properties.append({'leaseTime': ip_pools_dict['lease_time']})
                if ip_pools_dict['auto_config_dns'] != None: ip_pool_properties.append({'autoConfigureDNS': ip_pools_dict['auto_config_dns']})
                
                ip_pool_list.append({'ipPool': ip_pool_properties})
                
            dhcp_server_config.append({'ipPools': ip_pool_list})
                
            dhcp_server_xml = CreateXML("dhcp", dhcp_server_config )

            url='https://' + self.nsx_manager + '/api/4.0/edges/' + edge_id + '/dhcp/config'
            
            conn = httplib.HTTPSConnection(self.nsx_manager, 443)
            conn.request('PUT', url, dhcp_server_xml, self.headers)
            response = conn.getresponse()
            if response.status != 204:
                print str(response.status) + " DHCP Server configuration failed..." + str(response.read())
                exit(1)
            
        