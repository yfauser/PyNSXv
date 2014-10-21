__author__ = 'asteer'


class LogicalSwitch(object):
    def __init__(self, session):
        self._session = session

    def _request(self, method, uri, **kwargs):
        return self._session.do_request(method, uri, **kwargs)

    def get_all(self):
        return self._request('GET', '/api/2.0/vdn/virtualwires')

    def get_by_id(self, lswitch_id):
        return self._request('GET', '/api/2.0/vdn/virtualwires/' + lswitch_id)

    def get_id_by_name(self, lswitch_name):
        all_lswitches = self.get_all()
        return self._session.getFromXmlTree(all_lswitches, 'virtualWire', 'name', lswitch_name, 'objectId')
    
    def get_pg_id_by_name(self, lswitch_name, vds_name):
        all_lswitches = self.get_all()
        vds_context_backings = self._session.getSubXmlTree(all_lswitches, 'virtualWire', 'name', lswitch_name, 'vdsContextWithBacking')
        for vds_context_backing in vds_context_backings:
            if len(self._session.getFromXmlTree(vds_context_backing, 'switch', 'name', vds_name, 'name')) > 0:
                return self._session.listFromXmlTree(vds_context_backing, 'backingValue')[0]
        
    def create(self, scope_name, name, description='A Logical Switch', tenantId='undefined', controlPlaneMode=None):
        scope_id = self._session.networkScope.get_id_by_name(scope_name)[0]
        data = {'virtualWireCreateSpec':[]}
        data['virtualWireCreateSpec'].append({'name': name})
        data['virtualWireCreateSpec'].append({'description': description})
        data['virtualWireCreateSpec'].append({'tenantId': tenantId})
        if controlPlaneMode:
            data['virtualWireCreateSpec'].append({'controlPlaneMode': controlPlaneMode})

        return self._request('POST', '/api/2.0/vdn/scopes/' + scope_id + '/virtualwires', data=data)

    def delete(self, lswitch_id):
        return self._request('DELETE', '/api/2.0/vdn/virtualwires/' + lswitch_id)

    def delete_by_name(self, lswitch_name):
        ids = self.get_id_by_name(lswitch_name)
        if len(ids) > 1:
            raise Exception('lswitch name not unique')
        if len(ids) < 1:
            raise Exception('lswitch name not found')
        return self.delete(ids[0])
