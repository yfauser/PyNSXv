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

    def get_id_by_name(self, dlr_name):
        all_dlrs = self.get_all()
        return self._session.getFromXmlTree(all_dlrs, 'edgeSummary', 'name', dlr_name, 'objectId')

    def create(self, dc_name, cluster_name, ds_name, mgmt_net_name):
        vdr_appliance_properties = [{'resourcePoolId': self._session.getVcenterClusterMoid(dc_name, cluster_name)},
                                    {'datastoreId': self._session.getVcenterDatastoreMoid(dc_name, ds_name)}]
        vdr_appliance = [{'appliance': vdr_appliance_properties}]
        vdr_mgmt_interface_properties = [{'connectedToId': self._session.getVcenterNetworkMoid(dc_name, mgmt_net_name)}]

        data = {'edge':[]}
        data['edge'].append({'datacenterMoid': self._session.getVcenterDatacenterMoid(dc_name)})
        data['edge'].append({'type': 'distributedRouter'})
        data['edge'].append({'appliances': vdr_appliance})
        data['edge'].append({'mgmtInterface': vdr_mgmt_interface_properties})

        return self._request('POST', '/api/4.0/edges', data=data)

    def add_if(self, edge_name, if_name, ls_name, if_ip, if_mask, if_type):
        vdr_address_group_property = [{'primaryAddress': if_ip}, {'subnetMask': if_mask}]
        vdr_address_groups = [{'addressGroup': vdr_address_group_property}]
        vdr_interface_properties = [{'name': if_name},
                                    {'addressGroups': vdr_address_groups},
                                    {'mtu': '1500'},
                                    {'type': if_type},
                                    {'isConnected': 'true'},
                                    {'connectedToId': self._session.logicalSwitch.get_id_by_name(ls_name)[0]}]

        data = {'interfaces':[]}
        data['interfaces'].append({'interface': vdr_interface_properties})

        edge_id = self.get_id_by_name(edge_name)[0]

        parameters = {'action': 'patch'}

        return self._request('POST', '/api/4.0/edges/' + edge_id + '/interfaces',
                             params=parameters, data=data)

    def delete(self, dlr_id):
        return self._request('DELETE', '/api/4.0/edges/' + dlr_id)

    def delete_by_name(self, dlr_name):
        ids = self.get_id_by_name(dlr_name)
        if len(ids) > 1:
            raise Exception('dlr name not unique')
        if len(ids) < 1:
            raise Exception('dlr name not found')
        return self.delete(ids[0])
