'''
Created on 09.10.2014

@author: yfauser
'''
import PyNSXv.lib.session as session
import uuid

default_transport_zone_name = 'TZ1'
datacenter_name = 'YF-Homelab'
cluster_name = 'Edge-Cluster'
datastore_name = 'WDNASVMs'
managment_network_portgroup_name = 'VM Network'

# Create a new Session - debug is enabled so will be very noisy
s = session.Session('192.168.178.211', vcenterIp='192.168.178.210', debug=True)

# Create halfway unique ID Suffix to identify the Environment Instance
env_uuid = uuid.uuid4().__str__()
env_suffix = env_uuid.split('-')[4]
# list of network prefixes
net_prefixes = ['web-tier-','app-tier-','db-tier-','admin1-tier-','admin2-tier-', 'transit-net-']

# Create the needed logical switches and the empty ip interface deffinitions for the logical router 
env_ls_dict={}
for name in net_prefixes:
    env_ls_dict[name+env_suffix] = s.logicalSwitch.create(default_transport_zone_name, name+env_suffix)
                     
# Create a new distributer logical router
dlr = s.distributedRouter.create(datacenter_name, cluster_name, datastore_name, 'dlr-' + env_suffix, managment_network_portgroup_name)

# Craft the distributed router Interfaces properties
vdr_ipif_web = {'if_name': 'web-tier', 'ls_id': env_ls_dict['web-tier-'+env_suffix].find('objectId').text,
                'if_ip': '172.16.102.1', 'if_mask': '255.255.255.0', 'if_type': 'internal'}
vdr_ipif_app = {'if_name': 'web-app', 'ls_id': env_ls_dict['app-tier-'+env_suffix].find('objectId').text,
                'if_ip': '172.16.103.1', 'if_mask': '255.255.255.0', 'if_type': 'internal'}
vdr_ipif_db =  {'if_name': 'db-tier', 'ls_id': env_ls_dict['db-tier-'+env_suffix].find('objectId').text,
                'if_ip': '172.16.104.1', 'if_mask': '255.255.255.0', 'if_type': 'internal'}
vdr_ipif_admin1 = {'if_name': 'admin1-tier', 'ls_id': env_ls_dict['admin1-tier-'+env_suffix].find('objectId').text,
                   'if_ip': '192.168.10.1', 'if_mask': '255.255.255.0', 'if_type': 'internal'}
vdr_ipif_admin2 = {'if_name': 'admin2-tier', 'ls_id': env_ls_dict['admin2-tier-'+env_suffix].find('objectId').text,
                   'if_ip': '192.168.11.1', 'if_mask': '255.255.255.0', 'if_type': 'internal'}
vdr_ipif_transit = {'if_name': 'transit-net', 'ls_id': env_ls_dict['transit-net-'+env_suffix].find('objectId').text,
                    'if_ip': '172.16.101.1', 'if_mask': '255.255.255.0', 'if_type': 'internal'}
vdr_if_list = [vdr_ipif_web, vdr_ipif_app, vdr_ipif_db, vdr_ipif_admin1, vdr_ipif_admin2, vdr_ipif_transit]

# Configure and path the IP Interfaces of the VDR
vdr_name = 'dlr-' + env_suffix
vdr_interfaces = s.distributedRouter.add_if(vdr_name, vdr_if_list)


