'''
Created on 05.10.2014

@author: yfauser
'''
from PyNSXv.lib.servicesrouter import ServicesRouter

esg1 = ServicesRouter(nsx_manager="192.168.178.211")
esg1.staticRoute("edge-75", "192.168.178.1", "0")

static_route_dict1 = {'route_vnic_index': "0", 'route_network': '10.1.1.0/24', 'route_nexthop': '192.168.178.2'}
static_route_dict2 = {'route_description': 'This route is so special, it even gets a description', 
                      'route_vnic_index': "0", 
                      'route_network': '10.2.1.0/24', 
                      'route_nexthop': '192.168.178.2'}
static_routes_list = [static_route_dict1, static_route_dict2]

esg1.staticRoute("edge-75", "192.168.178.1", "0", static_routes_list=static_routes_list)
