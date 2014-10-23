'''
Created on 20.10.2014

@author: yfauser
'''
import PyNSXv.lib.session as session

env_suffix = '1069e4d74f3e'

s = session.Session('192.168.178.211', vcenterIp='192.168.178.210', debug=True)

vdr_name = 'vdr-' + env_suffix
vdr_id = s.distributedRouter.get_id_by_name(vdr_name)[0]

dhcp_server_list = ['172.16.101.3']
interface_index_list = ['10','11']

s.distributedRouter.DHCP_relay(vdr_id, dhcp_server_list, interface_index_list)
