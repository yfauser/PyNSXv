'''
Created on 07.10.2014

@author: yfauser
'''
from PyNSXv.lib.distribrouter import DistribRouter

vdr1 = DistribRouter(nsx_manager="192.168.178.211")
dhcp_server_list = ['172.16.101.1','172.16.102.2']
interface_index_list = ['10','11']
vdr1.DHCPrelay("edge-76", dhcp_server_list, interface_index_list)

