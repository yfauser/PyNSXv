'''
Created on 12.10.2014

@author: yfauser
'''
import PyNSXv.lib.session as session
# Create a new Session - debug is enabled so will be very noisy
s = session.Session('192.168.178.211', vcenterIp='192.168.178.210', debug=True)

esg_id = "edge-114"
esg_router_id = "172.16.101.3"

esg_ospf_area_dict1 = {'ospf_area': "0"}
esg_ospf_area_dict2 = {'ospf_area': "100",'ospf_area_type': "nssa", 'authentication_type': "password", 'authentication_password': "myGreatSecret"}
esg_ospf_area_dict3 = {'ospf_area': "100"}
esg_ospf_area_list = [esg_ospf_area_dict1, esg_ospf_area_dict3]
esg_ospf_interface_dict1 = {'vnic_index': "0", 'ospf_area': "0"}
esg_ospf_interface_dict2 = {'vnic_index': "1", 'ospf_area': "100", 'helloInterval': "23", 'priority': "200", 'cost': "22"}
esg_ospf_interface_dict3 = {'vnic_index': "1", 'ospf_area': "100"}
esg_ospf_interface_list = [esg_ospf_interface_dict1, esg_ospf_interface_dict3]

esg = s.servicesRouter.enable_OSPF(esg_id, esg_router_id, esg_ospf_area_list, esg_ospf_interface_list, default_originate="true")

vdr_id = "edge-113"
vdr_router_id = "172.16.101.2"
vdr_protocol_address = "172.16.101.2"
vdr_forwarding_address = "172.16.101.1"

vdr_ospf_area_list = [{'ospf_area': "100"}]
vdr_ospf_interface_list = [{'vnic_index': "2", 'ospf_area': "100"}]
vdr_ospf_redist_from_list = ['connected']

vdr = s.distributedRouter.enable_OSPF(vdr_id, vdr_router_id, vdr_protocol_address, vdr_forwarding_address, vdr_ospf_area_list, vdr_ospf_interface_list, vdr_ospf_redist_from_list)
