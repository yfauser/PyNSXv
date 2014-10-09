__author__ = 'asteer'

import PyNSXv.lib.session as session

datacenter_name = 'YF-Homelab'
cluster_name = 'Edge-Cluster'
datastore_name = 'WDNASVMs'
managment_network_portgroup_name = 'VM Network'
edge_id = 'blablabla'

# Create a new Session - debug is enabled so will be very noisy
# We need the also configure the vCenter session as we will  be using information from there
s = session.Session('192.168.178.211', vcenterIp='192.168.178.210', debug=True)

# Create a new distributer logical router
dlr = s.distributedRouter.create(datacenter_name, cluster_name, datastore_name, edge_id, managment_network_portgroup_name)

# And then delete it...
s.distributedRouter.delete(dlr.find('id').text)