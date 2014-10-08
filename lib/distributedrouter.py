__author__ = 'asteer'


class DistributedRouter:
    def __init__(self, session):
        self._session = session

    def _request(self, method, uri, **kwargs):
        return self._session.do_request(method, uri, **kwargs)

    def get_all(self):
        return self._request('GET', '/api/4.0/edges')

    def get_by_id(self, ldr_id):
        return self._request('GET', '/api/4.0/edges/' + ldr_id)

    def get_by_name(self, dlr_name):
        all_dlrs = self.get_all()
        return self._session.getFromXmlTree(all_dlrs, 'edgeSummary', 'name', dlr_name, 'objectId')

    def create(self, dc, cluster, ds, mgmt_net):
        vdr_appliance_properties = [{'resourcePoolId': self._session.getVcenterClusterMoid(dc, cluster)},
                                    {'datastoreId': self._session.getVcenterDatastoreMoid(dc, ds)}]
        vdr_appliance = [{'appliance': vdr_appliance_properties}]
        vdr_mgmt_interface_properties = [{'connectedToId': self._session.getVcenterNetworkMoid(dc, mgmt_net)}]

        data = {'edge':[]}
        data['edge'].append({'datacenterMoid': self._session.getVcenterDatacenterMoid(dc)})
        data['edge'].append({'type': 'distributedRouter'})
        data['edge'].append({'appliances': vdr_appliance})
        data['edge'].append({'mgmtInterface': vdr_mgmt_interface_properties})

        return self._request('POST', '/api/4.0/edges', data=data)

    def delete(self, dlr_id):
        return self._request('DELETE', '/api/4.0/edges/' + dlr_id)

    def delete_by_name(self, dlr_name):
        ids = self.get_by_name(dlr_name)
        if len(ids) > 1:
            raise Exception('dlr name not unique')
        if len(ids) < 1:
            raise Exception('dlr name not found')
        return self.delete(ids[0])
