'''
Created on 06.10.2014

@author: yfauser
'''
from PyNSXv.lib.xmlformater import ReadEdgeInterfaceXML

xml_content = "<?xml version=\"1.0\"?><interfaces><interface><label>vNic_1</label><name>interface1</name><addressGroups><addressGroup><primaryAddress>192.168.10.1</primaryAddress><subnetMask>255.255.255.0</subnetMask> </addressGroup></addressGroups><mtu>1500</mtu><type>uplink</type><isConnected>true</isConnected><index>1</index><connectedToId>dvportgroup-39</connectedToId><connectedToName>dvport-vlan-1</connectedToName></interface><interface><label>75649aea0000000a</label><name>interface10</name><addressGroups><addressGroup><primaryAddress>192.168.20.1</primaryAddress><subnetMask>255.255.255.0</subnetMask></addressGroup></addressGroups><mtu>1500</mtu><type>internal</type><isConnected>true</isConnected><index>10</index><connectedToId>dvportgroup-40</connectedToId><connectedToName>dvport-vlan-2</connectedToName></interface><interface><label>75649aea0000000b</label><name>interface-11</name><addressGroups><addressGroup><primaryAddress>192.168.50.1</primaryAddress><subnetMask>255.255.255.0</subnetMask></addressGroup></addressGroups><mtu>1500</mtu><type>internal</type><isConnected>true</isConnected><index>11</index><connectedToId>dvportgroup-37</connectedToId><connectedToName>DvSwitch2-DVUplinks-36</connectedToName></interface></interfaces>"

edge_interfaces_properties = ReadEdgeInterfaceXML(xml_content)

print edge_interfaces_properties

# Now let's retrieve the vnic_index from the interface name

test_dict = {}



