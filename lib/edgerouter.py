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

    def create(self, dc_name, cluster_name, ds_name, data):
        appliance_properties = [{'resourcePoolId': self._session.getVcenterClusterMoid(dc_name, cluster_name)},
                                    {'datastoreId': self._session.getVcenterDatastoreMoid(dc_name, ds_name)}]

        try:
            appliance = [x for x in data['edge'] if 'appliances' in x][0]
            index = data['edge'].index(appliance)
            data['edge'][index]['appliances'].append({'appliance': appliance_properties})
        except IndexError as e:
            data['edge'].append({'appliances': [{'appliance': appliance_properties}]})

        data['edge'].append({'datacenterMoid': self._session.getVcenterDatacenterMoid(dc_name)})

        return self._request('POST', '/api/4.0/edges', data=data)

    #TODO - rework this to treat all interfaces as list (even a list of one) can then process single / bulk additions
    def add_if(self, edge_name, if_name, ls_name, if_ip, if_mask, if_type, if_index=None):
        address_group_property = [{'primaryAddress': if_ip}, {'subnetMask': if_mask}]
        address_groups = [{'addressGroup': address_group_property}]
        interface_properties = [{'name': if_name},
                                    {'addressGroups': address_groups},
                                    {'mtu': '1500'},
                                    {'type': if_type},
                                    {'isConnected': 'true'},
                                    {'connectedToId': self._session.logicalSwitch.get_id_by_name(ls_name)[0]}]

        if if_index:
            interface_properties.append({'index': if_index})
            data = {'vnics':[]}
            data['vnics'].append({'vnic': interface_properties})
            path = '/vnics/'
        else:
            data = {'interfaces':[]}
            data['interfaces'].append({'interface': interface_properties})
            path = '/interfaces'

        edge_id = self.get_id_by_name(edge_name)[0]

        parameters = {'action': 'patch'}

        return self._request('POST', '/api/4.0/edges/' + edge_id + path,
                             params=parameters, data=data)

    def enable_OSPF(self,edge_id, router_id, protocol_address, forwarding_address, ospf_area,
                   ospf_vnic_index, ospf_vnic_helloInterval=10, ospf_vnic_deadInterval=40,
                   ospf_vnic_priority=128, ospf_vnic_cost=None, ospf_area_type='normal',
                   authentication_type=None, authentication_password='vmware123', ospf_redist_from_list=[]):
        ''' This method is used to configure the OSPF Area and the Interfaces used for/with OSPF
        edge_id: This is the edge id as returned by the create method
        router_id: This is the OSPF Router ID for the OSPF Database, usually this is set to be the same IP as the protocol_adress.
        protocol_address: This is the IP that the VDR uses to source OSPF Hellos, LSRs, etc. Basically this is the IP of the logical router control VM
        forwarding_address: This is the next hop IP for the advertised routes. This is the shared VIP of the VDR in the hypervisor kernel modules
        ospf_area: This is the OSPF Area ID, Mandatory and unique. Valid values are 0-4294967295
        ospf_vnic_index: This is the vnic Index of the VDR Uplink used for OSPF. With the VDR only one Interface can be used as an OSPF Interface. Example: '0'
        ospf_vnic_helloInterval: Optional. Default 10 sec. Valid values are 1-255
        ospf_vnic_deadInterval: Optional. Default 40 sec. Valid values are 1-65535
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

        if ospf_vnic_cost is not None:
            ospf_interface_config.append( {'cost': ospf_vnic_cost} )

        ospf_interfaces = [{'ospfInterface': ospf_interface_config}]
        routing_global_config = [{'routerId' : router_id }]
        ospf_authentication_config = [{'type': authentication_type}]

        if authentication_type is not None:
            ospf_authentication_config.append({'value': authentication_password})

        ospf_area_config = [{'ospfArea': [{'areaId': ospf_area},
                                          {'type': ospf_area_type},
                                          {'authentication': ospf_authentication_config}]}]

        if len(ospf_redist_from_list) > 0:
            ospf_redistribution_rules = []
            for redist_from in ospf_redist_from_list:
                ospf_redistribution_rules.append({redist_from: 'true'})
            ospf_redistribution_property = [{'enabled': 'true'},
                                            {'rules': [{'rule': [{'from': ospf_redistribution_rules},
                                                                 {'action': 'permit'}]}]}]
        else:
            ospf_redistribution_property = [{'enabled': 'false'}]

        ospf_config = [ {'enabled': 'true'}, {'forwardingAddress': forwarding_address},
                        {'protocolAddress': protocol_address}, {'ospfAreas': ospf_area_config},
                        {'ospfInterfaces': ospf_interfaces}, {'redistribution': ospf_redistribution_property} ]

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
