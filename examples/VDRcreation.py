'''
Created on 01.10.2014

@author: yfauser
'''
from PyNSXv.lib.distribrouter import DistribRouter

vdr1 = DistribRouter(nsx_manager="192.168.178.211")
create_edge_result = vdr1.create('datacenter-21','domain-c39','datastore-601','network-32')

print create_edge_result