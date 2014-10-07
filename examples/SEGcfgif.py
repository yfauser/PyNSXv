'''
Created on 04.10.2014

@author: yfauser
'''
from PyNSXv.lib.servicesrouter import ServicesRouter

esg1 = ServicesRouter(nsx_manager="192.168.178.211")
# cfgif will configure one single interface
esg1.cfgif(edge_id="edge-77", if_index="0", if_name="edge-77-interface0", ls_id="virtualwire-60", if_ip="192.168.178.198", if_mask="255.255.255.0", if_type="uplink")

if_dict_vnic1 = {'if_index': '1',
                 'if_name': 'edge-77-interface2',
                 'ls_id': 'virtualwire-61',
                 'if_ip': '172.16.102.2',
                 'if_mask': '255.255.255.0',
                 'if_type': 'internal'}

if_dict_vnic2 = {'if_index': '2',
                 'if_name': 'edge-77-interface3',
                 'ls_id': 'virtualwire-63',
                 'if_ip': '172.16.103.2',
                 'if_mask': '255.255.255.0',
                 'if_type': 'internal'}

if_list = [if_dict_vnic1,if_dict_vnic2]
esg1.cfgif_list(edge_id="edge-77", if_list=if_list)