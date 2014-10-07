__author__ = 'asteer'

import requests
import networkscope
import logicalswitch
import xml.dom.minidom as md
import xml.etree.ElementTree as et


class Session:
    def __init__(self, manager, username='admin', password='default', debug=False, verify=False,
                 protocol='https', base='/api/2.0'):
        self._manager = manager
        self._username = username
        self._password = password
        self._debug = debug
        self._verify = verify
        self._base = protocol + '://' + manager + base
        self._session = requests.Session()
        self._session.verify = self._verify
        self._session.auth = (self._username, self._password)

        if self._debug:
            import httplib
            httplib.HTTPConnection.debuglevel = 1

        # Wire up the namespaces
        self.networkScope = networkscope.NetworkScope(self)
        self.logicalSwitch = logicalswitch.LogicalSwitch(self)

    def do_request(self, method, path, data=None, headers=None):
        if data:
            headers = {'Content-Type': 'application/xml'}
            key = data.keys()[0]
            root = et.Element(key)
            for i in data[key]:
                et.SubElement(root, i.keys()[0]).text = i[i.keys()[0]]
            if self._debug:
                print "XML: "
                et.dump(root)
            data = et.tostring(root)
        response = self._session.request(method, self._base + path, headers=headers, data=data)
        response.raise_for_status()
        content = response.content
        if self._debug:
            if response.headers['Content-Type'] == 'application/xml':
                print md.parseString(content).toprettyxml()
            else:
                print content
        if response.headers['Content-Type'] == 'application/xml':
            return et.fromstring(content)
        else:
            return content

    def get_from_xml_string(self, xml_string, match_type, match_key, match_value, get):
        root = et.fromstring(xml_string)
        return self._get_generic_from_elementTree( root, match_type, match_key, match_value, get)

    def get_from_xml_tree(self, xml_tree, match_type, match_key, match_value, get):
        response = []
        root = xml_tree
        for i in root.iter(match_type):
            if i.find(match_key).text == match_value:
                response.append(i.find(get).text)
        return response
