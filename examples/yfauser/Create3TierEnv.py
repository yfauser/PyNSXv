'''
Created on 09.10.2014

@author: yfauser
'''
import PyNSXv.lib.session as session
import uuid

default_transport_zone_name = 'TZ1'
datacenter_name = 'YF-Homelab'
cluster_name = 'Nested-Edge-Cluster'
datastore_name = 'FauserNAS'
managment_network_portgroup_name = 'VM Network'

# Create a new Session - debug is enabled so will be very noisy
s = session.Session('192.168.178.211', vcenterIp='192.168.178.210', debug=True)

# Create halfway unique ID Suffix to identify the Environment Instance
env_uuid = uuid.uuid4().__str__()
env_suffix = env_uuid.split('-')[4]
# list of network prefixes
net_prefixes = ['web-tier-','app-tier-','db-tier-','admin1-tier-','admin2-tier-', 'transit-net-']

# Create the needed logical switches and the empty ip interface definitions for the logical router 
env_ls_dict={}
for name in net_prefixes:
    env_ls_dict[name+env_suffix] = s.logicalSwitch.create(default_transport_zone_name, name+env_suffix)
                     
# Create a new distributer logical router
vdr = s.distributedRouter.create(datacenter_name, cluster_name, datastore_name, 'dlr-' + env_suffix, managment_network_portgroup_name)

# Craft the distributed router Interfaces properties
vdr_ipif_web = {'if_name': 'web-tier', 'ls_id': env_ls_dict['web-tier-'+env_suffix].find('objectId').text,
                'if_ip': '172.16.102.1', 'if_mask': '255.255.255.0', 'if_type': 'internal'}
vdr_ipif_app = {'if_name': 'app-tier', 'ls_id': env_ls_dict['app-tier-'+env_suffix].find('objectId').text,
                'if_ip': '172.16.103.1', 'if_mask': '255.255.255.0', 'if_type': 'internal'}
vdr_ipif_db =  {'if_name': 'db-tier', 'ls_id': env_ls_dict['db-tier-'+env_suffix].find('objectId').text,
                'if_ip': '172.16.104.1', 'if_mask': '255.255.255.0', 'if_type': 'internal'}
vdr_ipif_admin1 = {'if_name': 'admin1-tier', 'ls_id': env_ls_dict['admin1-tier-'+env_suffix].find('objectId').text,
                   'if_ip': '192.168.10.1', 'if_mask': '255.255.255.0', 'if_type': 'internal'}
vdr_ipif_admin2 = {'if_name': 'admin2-tier', 'ls_id': env_ls_dict['admin2-tier-'+env_suffix].find('objectId').text,
                   'if_ip': '192.168.11.1', 'if_mask': '255.255.255.0', 'if_type': 'internal'}
vdr_ipif_transit = {'if_name': 'transit-net', 'ls_id': env_ls_dict['transit-net-'+env_suffix].find('objectId').text,
                    'if_ip': '172.16.101.1', 'if_mask': '255.255.255.0', 'if_type': 'uplink'}
vdr_if_list = [vdr_ipif_web, vdr_ipif_app, vdr_ipif_db, vdr_ipif_admin1, vdr_ipif_admin2, vdr_ipif_transit]

# Configure and path the IP Interfaces of the VDR
vdr_name = 'dlr-' + env_suffix
vdr_interfaces = s.distributedRouter.add_if(vdr_name, vdr_if_list)

# Create a new Services Edge Gateway
esg_name = 'esg-' + env_suffix
esg = s.servicesRouter.create(datacenter_name, cluster_name, datastore_name, 'esg-' + env_suffix, managment_network_portgroup_name, ssh_enabled="true")

# Craft the edge gateway services Interfaces Properties

uplink_portgroup_moid = s.getVcenterNetworkMoid(datacenter_name, managment_network_portgroup_name)

esg_ipif_uplink = {'if_index': '0',
                   'if_name': 'uplink-interface',
                   'ls_id': uplink_portgroup_moid,
                   'if_ip': '192.168.178.198',
                   'if_mask': '255.255.255.0',
                   'if_type': 'uplink'}

esg_ipif_transit = {'if_index': '1',
                    'if_name': 'transit-to-vdr',
                    'ls_id': env_ls_dict['transit-net-'+env_suffix].find('objectId').text,
                    'if_ip': '172.16.101.3',
                    'if_mask': '255.255.255.0',
                    'if_type': 'internal'}

esg_if_list = [esg_ipif_uplink, esg_ipif_transit]

# Configure the Edge Services Gateway Uplink and the Transit Link IP Interfaces
esg_interfaces = s.servicesRouter.add_if(esg_name, esg_if_list)

# In the next step we will configure OSPF on the VDR
vdr_uplink_vnic_index = s.getFromXmlString(vdr_interfaces, 'vnic' ,'name', vdr_ipif_transit['if_name'], 'index')
print "the uplink-name is " + vdr_ipif_transit['if_name']
print " and its vnic index is " + vdr_uplink_vnic_index[0]
print vdr_interfaces

vdr_router_id = "172.16.101.2"
vdr_protocol_address = "172.16.101.2"
vdr_forwarding_address = "172.16.101.1"
vdr_ospf_area_list = [{'ospf_area': "100"}]
vdr_ospf_interface_list = [{'vnic_index': vdr_uplink_vnic_index[0], 'ospf_area': "100"}]
vdr_ospf_redist_from_list = ['connected']

vdr = s.distributedRouter.enable_OSPF(vdr, vdr_router_id, vdr_protocol_address, vdr_forwarding_address, 
                                      vdr_ospf_area_list, vdr_ospf_interface_list, vdr_ospf_redist_from_list)

# In the next Step we are configuring OSPF on the ESG
esg_router_id = "172.16.101.3"
esg_ospf_area0_dict = {'ospf_area': "0"}
esg_ospf_area100_dict = {'ospf_area': "100"}
esg_ospf_area_list = [esg_ospf_area0_dict, esg_ospf_area100_dict]
esg_ospf_interface_uplink_dict = {'vnic_index': "0", 'ospf_area': "0"}
esg_ospf_interface_transit_dict = {'vnic_index': "1", 'ospf_area': "100"}
esg_ospf_interface_list = [esg_ospf_interface_transit_dict, esg_ospf_interface_uplink_dict]

esg = s.servicesRouter.enable_OSPF(esg, esg_router_id, esg_ospf_area_list, esg_ospf_interface_list, default_originate="true")

