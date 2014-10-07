__author__ = 'asteer'


class NetworkScope:
    def __init__(self, session):
        self._session = session

    def _request(self, method, uri, **kwargs):
        return self._session.do_request(method, uri, **kwargs)

    def get_all(self):
        return self._request('GET', '/api/2.0/vdn/scopes')

    def get_by_id(self, scope_id):
        return self._request('GET', '/api/2.0/vdn/scopes/' + scope_id)

    def get_by_name(self, scope_name):
        all_scopes = self.get_all()
        return self._session.get_from_xml_tree(all_scopes, 'vdnScope', 'name', scope_name, 'objectId')
