__author__ = 'asteer'


class EdgeRouter(object):
    def __init__(self, session):
        self._session = session

    def _request(self, method, uri, **kwargs):
        return self._session.do_request(method, uri, **kwargs)

    def get_all(self):
        return self._request('GET', '/api/4.0/edges')

    def get_by_id(self, ldr_id):
        return self._request('GET', '/api/4.0/edges/' + ldr_id)

    def get_id_by_name(self, edge_name):
        all_edges = self.get_all()
        return self._session.getFromXmlTree(all_edges, 'edgeSummary', 'name', edge_name, 'objectId')

    def create(self, dc_name, cluster_name, ds_name, edge_name, data):
        appliance_properties = [{'resourcePoolId': self._session.getVcenterClusterMoid(dc_name, cluster_name)},
                                    {'datastoreId': self._session.getVcenterDatastoreMoid(dc_name, ds_name)}]

        try:
            appliance = [x for x in data['edge'] if 'appliances' in x][0]
            index = data['edge'].index(appliance)
            data['edge'][index]['appliances'].append({'appliance': appliance_properties})
        except IndexError as e:
            data['edge'].append({'appliances': [{'appliance': appliance_properties}]})
        
        data['edge'].append({'datacenterMoid': self._session.getVcenterDatacenterMoid(dc_name)})
        if edge_name:
            data['edge'].append({'name': edge_name})

        return self._request('POST', '/api/4.0/edges', data=data)

    
    def add_if(self, edge_name, if_list):
        ''' This method creates the Interfaces on a router (DLR or Services Edge 
        edge_id: This is the edge id as returned by the create method
        if_list: This is a list of dictionaries containing interfes and their properties, these are the items in the dict:
            if_name: This is the human readable name set for the Interface
            ls_id: This is the logical switch id (aka vwire und virtual wire ID) as returned by the LogicalSwitch.Create Method
            if_ip: This is the Interface IP Address
            if_mask: This is the Interface Subnet Mask
            if_type: This is the type of Interface in NSX 6.x this can either be 'internal' or 'uplink', 
                     where uplink is the upstream interface that can have dynamic routing applied
            if_index: This is the edge interface Index. Values are 0..9
        '''
        data = None
        for interface in if_list:
            address_group_property = [ {'primaryAddress': interface['if_ip']}, {'subnetMask': interface['if_mask']} ]
            address_groups = [ {'addressGroup':  address_group_property} ]
            
            interface_properties = []
            interface_properties.append({'name': interface['if_name']})
            interface_properties.append({'addressGroups': address_groups})
            interface_properties.append({'mtu': '1500'})
            interface_properties.append({'type': interface['if_type']})
            interface_properties.append({'isConnected': 'true'})
            
            if ('if_index') in interface:
                interface_properties.append({'index': interface['if_index']})
                if data !=None: 
                    interface_properties.append({'portgroupId': interface['ls_id']})
                    data['vnics'].append({'vnic': interface_properties})
                else:
                    data = {'vnics':[]}
                    interface_properties.append({'portgroupId': interface['ls_id']})
                    data['vnics'].append({'vnic': interface_properties})
                path = '/vnics/'
            else:
                if data !=None:
                    interface_properties.append({'connectedToId': interface['ls_id']})
                    data['interfaces'].append({'interface': interface_properties})
                else:
                    data = {'interfaces':[]}
                    interface_properties.append({'connectedToId': interface['ls_id']})
                    data['interfaces'].append({'interface': interface_properties})
                path = '/interfaces/'
                
        edge_id = self.get_id_by_name(edge_name)[0]

        parameters = {'action': 'patch'}

        return self._request('POST', '/api/4.0/edges/' + edge_id + path,
                             params=parameters, data=data)

    def enable_OSPF(self, edge_id, router_id, ospf_area_list, ospf_interface_list, ospf_redist_from_list=None, default_originate=None, vdr_data=None):
        # TODO: At some point it would also be good to have the ability to set prefix filters for the redistribution
        ''' This method is used to configure the OSPF Areas, Interfaces, and with it enabled OSPF on the Edge Gateways or VDR Control VM
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
        default_originate: users can configure edge router to publish default route by setting it to true
        '''
        ospf_config = []
        ospf_config.append({'enabled': 'true'})
        
        if vdr_data != None: 
            for ospf_vdr_property in vdr_data:
                ospf_config.append(ospf_vdr_property)
            
        routing_global_config = [ {'routerId' : router_id } ]
            
        ospf_areas = []
        for ospf_area in ospf_area_list:
            if ('authentication_type') not in ospf_area: ospf_area['authentication_type'] = 'none'
            if ('ospf_area_type') not in ospf_area: ospf_area['ospf_area_type'] = 'normal'
            ospf_authentication_config = [ {'type': ospf_area['authentication_type']} ]
            if ospf_area['authentication_type'] != 'none': ospf_authentication_config.append( {'value': ospf_area['authentication_password'] } )
            ospf_area_properties = []
            ospf_area_properties.append({'areaId': ospf_area['ospf_area']})
            ospf_area_properties.append({'type': ospf_area['ospf_area_type']})
            ospf_area_properties.append({'authentication': ospf_authentication_config})
            ospf_areas.append( {'ospfArea': ospf_area_properties})
        
        ospf_config.append({'ospfAreas': ospf_areas})
        
        ospf_interfaces = []
        for interface in ospf_interface_list:
            if ('helloInterval') not in interface: interface['helloInterval']= '10'
            if ('deadInterval') not in interface: interface['deadInterval']= '40'
            if ('priority') not in interface: interface['priority']= '128'
            if ('cost') not in interface: interface['cost']= None
            ospf_interface_config = []
            ospf_interface_config.append({'vnic': interface['vnic_index']})
            ospf_interface_config.append({'areaId': interface['ospf_area']})
            ospf_interface_config.append({'helloInterval': interface['helloInterval']}) 
            ospf_interface_config.append({'deadInterval': interface['deadInterval']}) 
            ospf_interface_config.append({'priority': interface['priority']}) 
            if interface['cost'] != None: ospf_interface_config.append( {'cost': interface['cost'] } )
            ospf_interfaces.append( {'ospfInterface': ospf_interface_config} )
        
        ospf_config.append({'ospfInterfaces': ospf_interfaces})
        
        if ospf_redist_from_list==None:  ospf_redist_from_list=[]
        if len(ospf_redist_from_list) != 0:
            ospf_redistribution_rules = []
            for redist_from in ospf_redist_from_list:
                ospf_redistribution_rules.append({ redist_from: 'true'})
            ospf_redistribution_property = [{'enabled': 'true'}, {'rules': [ {'rule': [ {'from': ospf_redistribution_rules}, {'action': 'permit'} ] } ] } ]
        else: ospf_redistribution_property = [{'enabled': 'false'}]
            
        ospf_config.append({'redistribution': ospf_redistribution_property})
        
        if default_originate != None: 
            ospf_config.append({'defaultOriginate' : default_originate })     # Not sure if this also works for NSX 6.0, might be new in 6.1
        
        data = {'routing':[]}
        data['routing'].append({'routingGlobalConfig': routing_global_config})
        data['routing'].append({'ospf': ospf_config})

        return self._request('PUT', '/api/4.0/edges/' + edge_id + '/routing/config', data=data)


    def static_route(self, edge_id, default_gateway=None, default_gateway_vnic_index=None, static_routes_list=None):
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
        if default_gateway is not None:
            default_route_property=[{'description': 'default route set by PyNSXv'},
                                     {'vnic': default_gateway_vnic_index},
                                     {'gatewayAddress': default_gateway},
                                     {'mtu': '1500'}]
            routes_config.append( {'defaultRoute': default_route_property} )

        if static_routes_list is not None:
            static_routes=[]
            for static_route in static_routes_list:
                if 'route_description' not in static_route:
                    static_route['route_description'] = 'route set by PyNSXv'
                static_route_property=[{'description': static_route['route_description']},
                               {'vnic': static_route['route_vnic_index']},
                               {'network': static_route['route_network']},
                               {'nextHop': static_route['route_nexthop']},
                               {'mtu': '1500'}]
                static_routes.append({'route': static_route_property})
            routes_config.append( {'staticRoutes': static_routes} )

        data = {'staticRouting': routes_config}

        return self._request('PUT','/api/4.0/edges/' + edge_id + '/routing/config/static', data=data)


    def DHCP_relay(self, edge_id, dhcp_server_list, interface_index_list):
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

        data = {'relay': []}
        data['relay'].append({'relayServer': dhcp_server_ips})
        data['relay'].append({'relayAgents': relay_agents})

        return self._request('PUT', '/api/4.0/edges/' + edge_id + '/dhcp/config/relay', data=data)

    def delete(self, dlr_id):
        return self._request('DELETE', '/api/4.0/edges/' + dlr_id)

    def delete_by_name(self, dlr_name):
        ids = self.get_id_by_name(dlr_name)
        if len(ids) > 1:
            raise Exception('dlr name not unique')
        if len(ids) < 1:
            raise Exception('dlr name not found')
        return self.delete(ids[0])
