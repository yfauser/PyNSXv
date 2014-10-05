'''
Created on 05.10.2014

@author: yfauser
'''
from PyNSXv.lib.servicesrouter import ServicesRouter

esg1 = ServicesRouter(nsx_manager="192.168.178.211")

ospf_area_dict1 = {'ospf_area': "0"}
ospf_area_dict2 = {'ospf_area': "100",'ospf_area_type': "nssa", 'authentication_type': "password", 'authentication_password': "myGreatSecret"}
ospf_area_dict3 = {'ospf_area': "100"}
ospf_area_list = [ospf_area_dict1, ospf_area_dict3]
ospf_interface_dict1 = {'vnic_index': "0", 'ospf_area': "0"}
ospf_interface_dict2 = {'vnic_index': "2", 'ospf_area': "101", 'helloInterval': "23", 'priority': "200", 'cost': "22"}
ospf_interface_dict3 = {'vnic_index': "1", 'ospf_area': "100"}
ospf_interface_list = [ospf_interface_dict1, ospf_interface_dict3]
ospf_redistribution_from_list = ['connected']

esg1.enableOSPF("edge-75","172.16.101.3", ospf_area_list, ospf_interface_list, ospf_redistribution_from_list)
