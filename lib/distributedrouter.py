__author__ = 'asteer + yfauser'

import edgerouter


class DistributedRouter(edgerouter.EdgeRouter):
    def __init__(self, session):
        super(DistributedRouter, self).__init__(session)

    def create(self, dc_name, cluster_name, ds_name, edge_name, mgmt_net_name):
        vdr_mgmt_interface_properties = [{'connectedToId':
                                            self._session.getVcenterNetworkMoid(dc_name, mgmt_net_name)}]

        data = {'edge':[]}
        data['edge'].append({'type': 'distributedRouter'})
        data['edge'].append({'mgmtInterface': vdr_mgmt_interface_properties})

        return super(DistributedRouter, self).create(dc_name, cluster_name, ds_name, edge_name, data)
    
    def enable_OSPF(self, edge_id, router_id, protocol_address, forwarding_address, 
                   ospf_area_list, ospf_interface_list, ospf_redist_from_list=None, default_originate=None):
        ''' See edgerouter.py for the explanation of most of the parameters
        for the DistributedRouter there are two additional mandatory attributes:
        protocol_address: This is the IP that the VDR uses to source OSPF Hellos, LSRs, etc. 
                          Basically this is the IP of the logical router control VM
        forwarding_address: This is the next hop IP for the advertised routes. 
                          This is the shared VIP of the VDR in the hypervisor kernel modules
        '''
        vdr_ospf_data =[]
        vdr_ospf_data.append({'forwardingAddress': forwarding_address})
        vdr_ospf_data.append({'protocolAddress': protocol_address})
        
        return super(DistributedRouter, self).enable_OSPF(edge_id, router_id, ospf_area_list, ospf_interface_list,
                                                          ospf_redist_from_list, default_originate,
                                                          vdr_data=vdr_ospf_data)
        