__author__ = 'asteer'

import requests
import networkscope
import logicalswitch
import distributedrouter
import xmlformatter
import xml.dom.minidom as md
import xml.etree.ElementTree as et
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
import atexit

class Session:
    def __init__(self, manager, username='admin', password='default', debug=False, verify=False,
                 protocol='https', vc_ip=None, vc_user='root', vc_pass='vmware'):
        self._manager = manager
        self._username = username
        self._password = password
        self._debug = debug
        self._verify = verify
        self._base = protocol + '://' + manager
        self._session = requests.Session()
        self._session.verify = self._verify
        self._session.auth = (self._username, self._password)
        self._vc_ip = vc_ip
        self._vc_user = vc_user
        self._vc_pass = vc_pass

        if self._debug:
            import httplib
            httplib.HTTPConnection.debuglevel = 1

        self._si = None
        self._vc_content = None
        if vc_ip:
            self._si = SmartConnect(host=self._vc_ip, user=self._vc_user, pwd=self._vc_pass)
            if not self._si:
                raise Exception('vCenter connection failed')
            atexit.register(Disconnect, self._si)
            self._vc_content = self._si.RetrieveContent()

        # Wire up the namespaces
        self.networkScope = networkscope.NetworkScope(self)
        self.logicalSwitch = logicalswitch.LogicalSwitch(self)
        self.distributedRouter = distributedrouter.DistributedRouter(self)

    def do_request(self, method, path, data=None, headers=None):
        if data:
            headers = {'Content-Type': 'application/xml'}
            data = xmlformatter.CreateXML(data.keys()[0], data[data.keys()[0]])

            if self._debug:
                print md.parseString(data).toprettyxml()

        response = self._session.request(method, self._base + path, headers=headers, data=data)
        response.raise_for_status()
        content = response.content

        try:
            if self._debug:
                if response.headers['Content-Type'] == 'application/xml':
                    print md.parseString(content).toprettyxml()
                else:
                    print content
        except Exception as e:
            pass

        try:
            if 'Location' in response.headers:
                return self.do_request('GET', response.headers['Location'])
            elif 'content-type' in response.headers and response.headers['Content-Type'] == 'application/xml':
                return et.fromstring(response.content)
            else:
                return content
        except Exception as e:
            raise


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

    def get_vc_datacentermoid(self, dc_name):
        if self._vc_content == None:
            raise Exception('vCenter content not found')
        for dc in self._vc_content.rootFolder.childEntity:
            if dc.name == dc_name:
                return str(dc._moId)

    def get_vc_clustermoid(self, dc_name, cluster_name):
        if self._vc_content == None:
            raise Exception('vCenter content not found')
        for dc in self._vc_content.rootFolder.childEntity:
            if dc.name == dc_name:
                for rp in dc.hostFolder.childEntity:
                    if rp.name == cluster_name:
                        return str(rp._moId)

    def get_vc_datastoremoid(self, dc_name, ds_name):
        if self._vc_content == None:
            raise Exception('vCenter content not found')
        for dc in self._vc_content.rootFolder.childEntity:
            if dc.name == dc_name:
                for ds in dc.datastoreFolder.childEntity:
                    if ds.name == ds_name:
                        return str(ds._moId)

    def get_vc_networkmoid(self, dc_name, net_name):
        if self._vc_content == None:
            raise Exception('vCenter content not found')
        for dc in self._vc_content.rootFolder.childEntity:
            if dc.name == dc_name:
                for net in dc.networkFolder.childEntity:
                    if net.name == net_name:
                        return str(net._moId)
