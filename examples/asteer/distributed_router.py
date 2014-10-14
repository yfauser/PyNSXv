__author__ = 'asteer'

import lib.session as session

datacenter_name = 'EMEA'
cluster_name = 'Management'
datastore_name = 'server114-local-3'
managment_network_portgroup_name = 'ManagementVM'
edge_name = 'MyGreatDLR'

# Create a new Session - debug is enabled so will be very noisy
# We need the also configure the vCenter session as we will  be using information from there
s = session.Session('172.17.100.109', vcenterIp='172.17.100.110', debug=True)

# Create a new distributed logical router
dlr = s.distributedRouter.create(datacenter_name, cluster_name, datastore_name, edge_name, managment_network_portgroup_name)

# And then delete it...
#s.distributedRouter.delete(dlr.find('id').text)