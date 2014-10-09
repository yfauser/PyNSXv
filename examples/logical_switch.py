__author__ = 'asteer'

import PyNSXv.lib.session as session

default_transport_zone_name = 'TZ1'

# Create a new Session - debug is enabled so will be very noisy
s = session.Session('192.168.178.211', debug=True)

# Create a new logical switch
lswitch_xml_tree = s.logicalSwitch.create(default_transport_zone_name, 'new-lswitch10')

# And then delete it...
s.logicalSwitch.delete(lswitch_xml_tree.find('objectId').text)
