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

# Create the needed logical switches 
env_ls_dict={}
for name in ['web-tier-','app-tier-','db-tier-','admin1-tier-','admin2-tier-']:
    env_ls_dict[name+env_suffix] = s.logicalSwitch.create(default_transport_zone_name, name+env_suffix)
                     
# Create a new distributer logical router
dlr = s.distributedRouter.create(datacenter_name, cluster_name, datastore_name, 'dlr-' + env_suffix, managment_network_portgroup_name)







