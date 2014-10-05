'''
Created on 05.10.2014

@author: yfauser
'''
from PyNSXv.lib.distribrouter import DistribRouter

vdr1 = DistribRouter(nsx_manager="192.168.178.211")
vdr1.enableOSPF("edge-74", "172.16.101.2", "172.16.101.2", "172.16.101.1", "100", "2")
