'''
Created on 12.10.2014

@author: yfauser
'''
# Create a new Session - debug is enabled so will be very noisy
import PyNSXv.lib.session as session

s = session.Session('192.168.178.211', vcenterIp='192.168.178.210', debug=True)

vdr_interfaces = s.distributedRouter.get_interfaces_by_id('edge-117')

vdr_uplink_vnic_index = s.getFromXmlTree(vdr_interfaces, 'interface' ,'name', 'transit-net', 'index')

print vdr_uplink_vnic_index
