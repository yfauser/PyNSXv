'''
Created on 21.10.2014

@author: yfauser
'''
import PyNSXv.lib.session as session

default_transport_zone_name = 'TZ1'
datacenter_name = 'YF-Homelab'
cluster_name = 'Nested-Edge-Cluster'
datastore_name = 'FauserNAS'
managment_network_portgroup_name = 'VM Network'
lswitch_name = "transit-net-1606dcd989df"
vds_name = "Transport-vDS"

# Create a new Session - debug is enabled so will be very noisy
s = session.Session('192.168.178.211', vcenterIp='192.168.178.210', debug=True)
vds_pg_id = s.logicalSwitch.get_pg_id_by_name(lswitch_name, vds_name)

print s.getVcenterPGname(datacenter_name, vds_pg_id)

s.changeVcenterPGname(datacenter_name, vds_pg_id, "Adrian rocks!")
    
print s.getVcenterPGname(datacenter_name, vds_pg_id)