'''
Created on 01.10.2014

@author: yfauser
'''
from PyNSXv.lib.logicalswitch import LogicalSwitch

ls1 = LogicalSwitch(nsx_manager="192.168.178.211")
ls_create_result = ls1.create("TestLS", vdn_scope="vdnscope-2")
print ls_create_result

