__author__ = 'asteer'

import edgerouter


class DistributedRouter(edgerouter.EdgeRouter):
    def __init__(self, session):
        super(DistributedRouter, self).__init__(session)

    def create(self, dc_name, cluster_name, ds_name, mgmt_net_name):
        vdr_mgmt_interface_properties = [{'connectedToId':
                                            self._session.getVcenterNetworkMoid(dc_name, mgmt_net_name)}]

        data = {'edge':[]}
        data['edge'].append({'type': 'distributedRouter'})
        data['edge'].append({'mgmtInterface': vdr_mgmt_interface_properties})

        return super(DistributedRouter, self).create(dc_name, cluster_name, ds_name, data)