'''
Created on 23.10.2014

@author: yfauser
'''
import PyNSXv.lib.session as session

env_suffix = 'ca937f6ae60f'

s = session.Session('192.168.178.211', vcenterIp='192.168.178.210', debug=True)

vdr_name = 'vdr-' + env_suffix
vdr_id = s.distributedRouter.get_id_by_name(vdr_name)[0]

esg_name = 'esg-' + env_suffix
esg_id = s.distributedRouter.get_id_by_name(esg_name)[0]

default_policy = 'accept'
default_logging = 'true'

s.distributedRouter.fwRuleTable(vdr_id, default_policy, default_logging)
s.servicesRouter.fwRuleTable(esg_id, default_policy, default_logging)
