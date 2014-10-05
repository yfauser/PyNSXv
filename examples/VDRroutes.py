'''
Created on 05.10.2014

@author: yfauser
'''
from PyNSXv.lib.distribrouter import DistribRouter

vdr1 = DistribRouter(nsx_manager="192.168.178.211")
vdr1.staticRoute("edge-74", "172.16.101.3", "2")

static_route_dict1 = {'route_vnic_index': "11", 'route_network': '10.3.1.0/24', 'route_nexthop': '172.16.102.2'}
static_route_dict2 = {'route_description': 'This route is so special, it even gets a description', 
                      'route_vnic_index': "12", 
                      'route_network': '10.4.1.0/24', 
                      'route_nexthop': '172.16.103.2'}
static_routes_list = [static_route_dict1, static_route_dict2]

vdr1.staticRoute("edge-74", "172.16.101.3", "2", static_routes_list=static_routes_list)