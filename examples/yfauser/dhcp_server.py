'''
Created on 23.10.2014

@author: yfauser
'''
import PyNSXv.lib.session as session

datacenter_name = 'YF-Homelab'
env_suffix = 'fb980e79c1e4'

s = session.Session('192.168.178.211', vcenterIp='192.168.178.210', debug=True)

vm_moid1 = s.getVcenterVMMoid(datacenter_name, 'XP-Test-1')
vm_moid2 = s.getVcenterVMMoid(datacenter_name, 'Windows-Server')

static_binding1 = {'mac_address': '00:0c:f6:33:33:33', 'hostname': 'MyComputer','ip_address': '172.16.101.11'}
static_binding2 = {'vm_id': vm_moid2, 'vm_vnic_id': '0','hostname': 'WindowsServer','ip_address': '172.16.101.12'}
static_binding3 = {'vm_id': vm_moid1, 'vm_vnic_id': '0', 
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
ip_pool2 = {'ip_range': '172.16.200.50-172.16.200.70', 
            'default_gateway': '172.16.200.254',
            'domain_name': 'funnyname.org',
            'primary_ns': '192.168.178.230',
            'secondary_ns': '8.8.8.8',
            'lease_time': '3600',
            'auto_config_dns': 'false'}
ip_pool_list = [ip_pool1,ip_pool2]

esg_name = 'esg-' + env_suffix
esg_id = s.servicesRouter.get_id_by_name(esg_name)[0]

s.servicesRouter.DHCP_server(esg_id, static_binding_list, ip_pool_list)
