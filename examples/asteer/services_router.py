'''
Created on 09.10.2014

@author: yfauser
'''
import PyNSXv.lib.session as session

datacenter_name = 'YF-Homelab'
cluster_name = 'Management-Cluster'
datastore_name = 'WDNASVMs'
first_interface_portgroup_name = 'VM Network'
edge_id = 'MyGreatServicesEdge'

# Create a new Session - debug is enabled so will be very noisy
# We need the also configure the vCenter session as we will  be using information from there
s = session.Session('192.168.178.211', vcenterIp='192.168.178.210', debug=True)

# Create a new distributer logical router
esg = s.servicesRouter.create(datacenter_name, cluster_name, datastore_name, edge_id, first_interface_portgroup_name)



