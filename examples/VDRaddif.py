'''
Created on 04.10.2014

@author: yfauser
'''
from PyNSXv.lib.distribrouter import DistribRouter

vdr1 = DistribRouter(nsx_manager="192.168.178.211")
# addif will create one single interface and attach it
vdr1.addif(edge_id="edge-74", if_name="edge-74-interface0", ls_id="virtualwire-56", if_ip="172.16.101.1", if_mask="255.255.255.0", if_type="uplink")

# addif_list can be used to create multiple Interface in one shot by passing a List of Interfaces with their properties as dictionary 
if_dict_int1 = {'if_name': 'edge-74-interface1',
                'ls_id': 'virtualwire-58',
                'if_ip': '172.16.102.1',
                'if_mask': '255.255.255.0',
                'if_type': 'internal'}

if_dict_int2 = {'if_name': 'edge-74-interface2',
                'ls_id': 'virtualwire-59',
                'if_ip': '172.16.103.1',
                'if_mask': '255.255.255.0',
                'if_type': 'internal'}

if_list = [if_dict_int1,if_dict_int2]
vdr1.addif_list(edge_id="edge-74", if_list=if_list)