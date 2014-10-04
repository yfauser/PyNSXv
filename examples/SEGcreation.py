'''
Created on 04.10.2014

@author: yfauser
'''
from PyNSXv.lib.servicesrouter import ServicesRouter

esg1 = ServicesRouter(nsx_manager="192.168.178.211")
create_edge_result = esg1.create('testesg','datacenter-21','domain-c39','datastore-601','network-32')

print create_edge_result
