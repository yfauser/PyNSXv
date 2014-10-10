'''
Created on 09.10.2014

@author: yfauser
'''
import PyNSXv.lib.session as session

default_transport_zone_name = 'TZ1'

# Create a new Session - debug is enabled so will be very noisy
s = session.Session('192.168.178.211', debug=True)

env_suffix = 'a2b594486cf9'

# delete the Service Gateway Edge
s.servicesRouter.delete_by_name('esg-' + env_suffix)

# delete the Distributed Logical Router
s.distributedRouter.delete_by_name('dlr-' + env_suffix)

# list of network prefixes
net_prefixes = ['web-tier-','app-tier-','db-tier-','admin1-tier-','admin2-tier-', 'transit-net-']

# delete the logical switches
for name in net_prefixes:
    ls_name = name + env_suffix
    s.logicalSwitch.delete_by_name(ls_name)



