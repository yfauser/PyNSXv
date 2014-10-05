'''
Created on 05.10.2014

@author: yfauser
'''
from PyNSXv.lib.servicesrouter import ServicesRouter

esg1 = ServicesRouter(nsx_manager="192.168.178.211")
esg1.addOSPFArea("edge-75","172.16.101.3" , "100")

ospf_area_dict1 = {'ospf_area': "102"}
ospf_area_dict2 = {'ospf_area': "103",'ospf_area_type': "nssa", 'authentication_type': "password", 'authentication_password': "myGreatSecret"}
ospf_area_list = [ospf_area_dict1, ospf_area_dict2]

esg1.addOSPFArealist("edge-75","172.16.101.3", ospf_area_list)