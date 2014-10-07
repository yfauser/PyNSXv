'''
Created on 07.10.2014

@author: yfauser
'''
from PyNSXv.lib.distribrouter import DistribRouter
from PyNSXv.lib.servicesrouter import ServicesRouter

vdr1 = DistribRouter(nsx_manager="192.168.178.211")
dhcp_server_list = ['172.16.101.3']
interface_index_list = ['10','11']
vdr1.DHCPrelay("edge-76", dhcp_server_list, interface_index_list)

esg1 = ServicesRouter(nsx_manager="192.168.178.211")

static_binding1 = {'mac_address': '00:0c:f6:33:33:33', 'hostname': 'MyComputer','ip_address': '172.16.101.11'}
static_binding2 = {'vm_id': 'vm-981', 'vm_vnic_id': '0','hostname': 'WindowsServer','ip_address': '172.16.101.12'}
static_binding3 = {'vm_id': 'vm-405', 'vm_vnic_id': '0', 
                   'hostname': 'OldXP-VM', 
                   'ip_address': '172.16.101.13', 
                   'default_gateway': '172.16.101.254',
                   'domain_name': 'funnyname.org',
                   'primary_ns': '192.168.178.230',
                   'secondary_ns': '8.8.8.8',
                   'lease_time': '3600',
                   'auto_config_dns': 'false'}
static_binding_list = [static_binding1,static_binding2,static_binding3]

ip_pool1 = {'ip_range': '172.16.101.50-172.16.101.70'}
ip_pool2 = {'ip_range': '172.16.106.50-172.16.106.70', 
            'default_gateway': '172.16.106.254',
            'domain_name': 'funnyname.org',
            'primary_ns': '192.168.178.230',
            'secondary_ns': '8.8.8.8',
            'lease_time': '3600',
            'auto_config_dns': 'false'}
ip_pool_list = [ip_pool1,ip_pool2]

esg1.DHCPServer("edge-77", static_binding_dict_list=static_binding_list,ip_pools_dict_list=ip_pool_list)



