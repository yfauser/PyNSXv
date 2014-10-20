'''
Created on 12.10.2014

@author: yfauser
'''
# Create a new Session - debug is enabled so will be very noisy
import PyNSXv.lib.session as session

env_suffix = 'd6138b839e1b'

s = session.Session('192.168.178.211', vcenterIp='192.168.178.210', debug=True)

# Craft the distributed router Interfaces properties
vdr_ipif_web = {'if_name': 'web-tier', 'ls_id': 'virtualwire-257',
                'if_ip': '172.16.102.1', 'if_mask': '255.255.255.0', 'if_type': 'internal'}
vdr_ipif_app = {'if_name': 'app-tier', 'ls_id': 'virtualwire-258',
                'if_ip': '172.16.103.1', 'if_mask': '255.255.255.0', 'if_type': 'internal'}
vdr_ipif_db =  {'if_name': 'db-tier', 'ls_id': 'virtualwire-259',
                'if_ip': '172.16.104.1', 'if_mask': '255.255.255.0', 'if_type': 'internal'}
vdr_ipif_admin1 = {'if_name': 'admin1-tier', 'ls_id': 'virtualwire-260',
                   'if_ip': '192.168.10.1', 'if_mask': '255.255.255.0', 'if_type': 'internal'}
vdr_ipif_admin2 = {'if_name': 'admin2-tier', 'ls_id': 'virtualwire-261',
                   'if_ip': '192.168.11.1', 'if_mask': '255.255.255.0', 'if_type': 'internal'}
vdr_ipif_transit = {'if_name': 'transit-net', 'ls_id': 'virtualwire-262',
                    'if_ip': '172.16.101.1', 'if_mask': '255.255.255.0', 'if_type': 'uplink'}
vdr_if_list = [vdr_ipif_web, vdr_ipif_app, vdr_ipif_db, vdr_ipif_admin1, vdr_ipif_admin2, vdr_ipif_transit]

# Configure and path the IP Interfaces of the VDR
vdr_name = 'vdr-' + env_suffix
vdr_interfaces = s.distributedRouter.add_if(vdr_name, vdr_if_list)

# In the next step we will configure OSPF on the VDR
vdr_uplink_vnic_index = s.getFromXmlTree(vdr_interfaces, 'interface' ,'name', vdr_ipif_transit['if_name'], 'index')
print "the uplink-name is " + vdr_ipif_transit['if_name']
print " and its vnic index is " + vdr_uplink_vnic_index[0]

vdr_router_id = "172.16.101.2"
vdr_protocol_address = "172.16.101.2"
vdr_forwarding_address = "172.16.101.1"
vdr_ospf_area_list = [{'ospf_area': "100"}]
vdr_ospf_interface_list = [{'vnic_index': vdr_uplink_vnic_index[0], 'ospf_area': "100"}]
vdr_ospf_redist_from_list = ['connected']

vdr = s.distributedRouter.enable_OSPF('edge-121', vdr_router_id, vdr_protocol_address, vdr_forwarding_address, 
                                      vdr_ospf_area_list, vdr_ospf_interface_list, vdr_ospf_redist_from_list)


