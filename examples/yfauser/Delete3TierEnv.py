'''
Created on 09.10.2014

@author: yfauser
'''
import PyNSXv.lib.session as session

default_transport_zone_name = 'TZ1'

# Create a new Session - debug is enabled so will be very noisy
s = session.Session('192.168.178.211', debug=True)

env_suffix = '16f184086c1f'

# delete the Service Gateway Edge
try:
    s.servicesRouter.delete_by_name('esg-' + env_suffix)
except:
    print "Error deleting Edge Services Gateway, might not be found"

# delete the Distributed Logical Router
try:
    s.distributedRouter.delete_by_name('vdr-' + env_suffix)
except:
    print "Error deleting VDR Control VM, might not be found"    

# list of network prefixes
net_prefixes = ['web-tier-','app-tier-','db-tier-','admin1-tier-','admin2-tier-', 'transit-net-']

# delete the logical switches
for name in net_prefixes:
    ls_name = name + env_suffix
    try:
        s.logicalSwitch.delete_by_name(ls_name)
    except:
        print "error while deleting logical switch " + ls_name + " might not be not found"



