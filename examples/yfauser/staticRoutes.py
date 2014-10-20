'''
Created on 20.10.2014

@author: yfauser
'''
import PyNSXv.lib.session as session

env_suffix = '924d43ec3631'

s = session.Session('192.168.178.211', vcenterIp='192.168.178.210', debug=True)

esg_name = 'esg-' + env_suffix
esg_id = s.servicesRouter.get_id_by_name(esg_name)[0]

static_route_dict1 = {'route_vnic_index': "0", 'route_network': '10.1.1.0/24', 'route_nexthop': '192.168.178.2'}
static_route_dict2 = {'route_description': 'This route is so special, it even gets a description', 
                      'route_vnic_index': "0", 
                      'route_network': '10.2.1.0/24', 
                      'route_nexthop': '192.168.178.2'}
static_routes_list = [static_route_dict1, static_route_dict2]

s.servicesRouter.static_route(esg_id, "192.168.178.1", "0", static_routes_list)

