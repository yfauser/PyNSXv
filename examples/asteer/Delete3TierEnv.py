'''
Created on 09.10.2014

@author: yfauser
'''
import PyNSXv.lib.session as session

default_transport_zone_name = 'TZ1'

# Create a new Session - debug is enabled so will be very noisy
s = session.Session('192.168.178.211', debug=True)

env_suffix = 'aa8a45c4772f'

# delete the logical switches
for name in ['web-tier-','app-tier-','db-tier-','admin1-tier-','admin2-tier-']:
    ls_name = name + env_suffix
    s.logicalSwitch.delete_by_name(ls_name)

