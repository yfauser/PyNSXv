'''
Created on 09.10.2014

@author: yfauser
'''
import lib.session as session

datacenter_name = 'EMEA'
cluster_name = 'Management'
datastore_name = 'server114-local-3'
first_interface_portgroup_name = 'ManagementVM'
edge_name = 'MyGreatServicesEdge'

# Create a new Session - debug is enabled so will be very noisy
# We need the also configure the vCenter session as we will  be using information from there
s = session.Session('172.17.100.109', vcenterIp='172.17.100.110', debug=True)

# Create a new distributer logical router
esg = s.servicesRouter.create(datacenter_name, cluster_name, datastore_name, edge_name, first_interface_portgroup_name)



